import json
import mimetypes
import os
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Max, Min, Sum
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from . import i18n
from .models import Guest, GuestUpload, Rsvp, Wedding, Wish
from .serializers import (
    GuestSerializer,
    GuestUploadSerializer,
    RsvpCreateSerializer,
    WeddingSerializer,
    WishCreateSerializer,
    WishSerializer,
)

ALLOWED_PREFIXES = ("image/", "video/")
# iOS ba'zan HEIC/HEIF uchun bo'sh yoki noto'g'ri MIME yuboradi — kengaytma bo'yicha ham tekshiramiz
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".gif", ".tiff", ".dng", ".raw",
    ".mp4", ".mov", ".m4v", ".avi", ".mkv", ".hevc", ".3gp", ".webm",
}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".hevc", ".3gp", ".webm"}


class UploadThrottle(AnonRateThrottle):
    scope = "upload"


class RsvpThrottle(AnonRateThrottle):
    scope = "rsvp"


def get_wedding():
    wedding = Wedding.objects.filter(is_active=True).prefetch_related("timeline", "gallery").first()
    if not wedding:
        raise Http404("To'y sozlamalari hali kiritilmagan.")
    return wedding


# ------------------------------------------------------------------ sahifa


def invitation_page(request):
    """
    Taklifnoma sahifasi. Matn va rasmlar serverda render qilinadi —
    shuning uchun sahifa darhol ochiladi va Telegram havola preview'ida
    haqiqiy ismlar ko'rinadi.
    """
    wedding = (
        Wedding.objects.filter(is_active=True)
        .prefetch_related("timeline", "gallery")
        .first()
    )
    if not wedding:
        return render(request, "site/empty.html", status=200)

    code = request.GET.get("g", "").strip()
    guest = None
    if code:
        guest = Guest.objects.filter(wedding=wedding, code__iexact=code).first()
        if guest:
            Guest.objects.filter(pk=guest.pk).update(
                open_count=guest.open_count + 1,
                opened_at=guest.opened_at or timezone.now(),
            )

    lang = i18n.clean_lang(request.GET.get("lang"))
    L = i18n.ui(lang, wedding)

    local = timezone.localtime(wedding.event_at)
    has_point = wedding.latitude is not None and wedding.longitude is not None
    place_text = f"{wedding.venue_name} {wedding.venue_address}".strip()

    # Google Maps — API kaliti kerak emas.
    # Koordinata bo'lsa aynan o'sha nuqta, bo'lmasa manzil matni bo'yicha.
    if has_point:
        point = f"{wedding.latitude},{wedding.longitude}"
        map_embed = f"https://www.google.com/maps?q={point}&hl=uz&z=17&output=embed"
        map_href = wedding.map_url or (
            f"https://www.google.com/maps/search/?api=1&query={point}"
        )
    elif place_text:
        query = quote(place_text)
        map_embed = f"https://www.google.com/maps?q={query}&hl=uz&z=15&output=embed"
        map_href = wedding.map_url or (
            f"https://www.google.com/maps/search/?api=1&query={query}"
        )
    else:
        map_embed = None
        map_href = wedding.map_url

    photos = list(wedding.gallery.all())
    wish_list = list(wedding.wishes.filter(is_visible=True)[:50])

    # Tanlangan tildagi matnlar. Inglizchasi bo'sh bo'lsa o'zbekchasi chiqadi.
    tx = {
        "groom": i18n.pick(wedding, "groom_name", lang),
        "bride": i18n.pick(wedding, "bride_name", lang),
        "invite_text": i18n.pick(wedding, "invite_text", lang),
        "venue_name": i18n.pick(wedding, "venue_name", lang),
        "venue_address": i18n.pick(wedding, "venue_address", lang),
        "dress_code": i18n.pick(wedding, "dress_code", lang),
        "thanks_title": i18n.pick(wedding, "thanks_title", lang) or L["dear"],
        "thanks_text": i18n.pick(wedding, "thanks_text", lang),
        "upload_hint": i18n.pick(wedding, "upload_hint", lang) or L["upload_default_hint"],
    }

    story = [
        {
            "title": i18n.pick(e, "title", lang),
            "date_label": i18n.pick(e, "date_label", lang),
            "text": i18n.pick(e, "text", lang),
        }
        for e in wedding.timeline.all()
    ]

    # Mehmonning shaxsiy rasmi va musiqasi bo'lsa o'sha, bo'lmasa umumiysi
    hero_file = (guest.hero_image if guest and guest.hero_image else wedding.hero_image)
    music_file = (guest.music if guest and guest.music else wedding.music)
    hero_url = hero_file.url if hero_file else ""
    music_url = music_file.url if music_file else ""

    duas = [
        {
            "title": i18n.pick(d, "title", lang),
            "arabic": d.arabic,
            "transliteration": d.transliteration,
            "meaning": i18n.pick(d, "meaning", lang),
            "source": d.source,
        }
        for d in wedding.duas.filter(is_visible=True)
    ]

    # Til tugmasi bosilganda mehmon kodi yo'qolmasligi kerak
    keep = f"g={quote(code)}&" if code else ""

    contacts = [
        {"name": n, "phone": p, "tel": "".join(ch for ch in p if ch.isdigit() or ch == "+")}
        for n, p in (
            (wedding.contact_one_name, wedding.contact_one_phone),
            (wedding.contact_two_name, wedding.contact_two_phone),
        )
        if p
    ]
    initials = (tx["groom"][:1] + tx["bride"][:1]).upper()
    rsvp_heading = (
        L["rsvp_title_named"].replace("{name}", guest.name) if guest else L["rsvp_title"]
    )

    return render(
        request,
        "site/index.html",
        {
            "w": wedding,
            "guest": guest,
            "guest_code": code,
            "lang": lang,
            "L": L,
            "hero_url": hero_url,
            "music_url": music_url,
            "tx": tx,
            "link_uz": f"?{keep}lang=uz",
            "link_en": f"?{keep}lang=en",
            "timeline": story,
            "duas": duas,
            "gallery": photos,
            "wishes": wish_list,
            "wishes_json": json.dumps(
                [{"id": x.id, "name": x.name, "text": x.text} for x in wish_list],
                ensure_ascii=False,
            ),
            "event_iso": wedding.event_at.isoformat(),
            "event_date": i18n.format_date(local, lang),
            "event_weekday": i18n.weekday(local, lang),
            "event_time": local.strftime("%H:%M"),
            "map_href": map_href,
            "map_embed": map_embed,
            "max_upload_mb": settings.MAX_UPLOAD_SIZE_MB,
            "site_url": settings.SITE_URL,
            "contacts": contacts,
            "rsvp_heading": rsvp_heading,
            "initials": initials,
            "event_day": local.day,
            "event_month": i18n.MONTHS[lang][local.month - 1],
            "event_year": local.year,
        },
    )



# ------------------------------------------------------------------ ochiq API


@api_view(["GET"])
def wedding_detail(request):
    """Taklifnomaning barcha ma'lumoti. ?g=KOD bo'lsa mehmon ismi ham qaytadi."""
    wedding = get_wedding()
    data = WeddingSerializer(wedding, context={"request": request}).data

    code = request.GET.get("g", "").strip()
    data["guest"] = None
    if code:
        guest = Guest.objects.filter(wedding=wedding, code__iexact=code).first()
        if guest:
            data["guest"] = GuestSerializer(guest).data
            Guest.objects.filter(pk=guest.pk).update(
                open_count=guest.open_count + 1,
                opened_at=guest.opened_at or timezone.now(),
            )
    return Response(data)


@api_view(["POST"])
@throttle_classes([RsvpThrottle])
def rsvp_create(request):
    wedding = get_wedding()
    if not wedding.rsvp_open:
        return Response(
            {"detail": "Javob qabul qilish yopilgan."}, status=status.HTTP_403_FORBIDDEN
        )

    serializer = RsvpCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data.pop("guest_code", "")
    guest = Guest.objects.filter(wedding=wedding, code__iexact=code).first() if code else None

    if not serializer.validated_data.get("attending"):
        serializer.validated_data["seats"] = 0

    rsvp = Rsvp.objects.create(wedding=wedding, guest=guest, **serializer.validated_data)
    return Response(
        {"ok": True, "id": rsvp.id, "attending": rsvp.attending},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@throttle_classes([UploadThrottle])
def upload_create(request):
    """
    Bitta faylni qabul qiladi. Fayl asl holida saqlanadi:
    siqilmaydi, o'lchami o'zgarmaydi, formati aylantirilmaydi.
    """
    wedding = get_wedding()
    if not wedding.uploads_open:
        return Response(
            {"detail": "Rasm yuklash hozircha yopiq."}, status=status.HTTP_403_FORBIDDEN
        )

    upload = request.FILES.get("file")
    if not upload:
        return Response({"detail": "Fayl yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

    name = (request.data.get("uploader_name") or "").strip()
    if len(name) < 2:
        return Response(
            {"detail": "Ismingizni yozing — rasmlar shu nom bilan saqlanadi."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ext = os.path.splitext(upload.name)[1].lower()
    ctype = (upload.content_type or "").lower()
    type_ok = ctype.startswith(ALLOWED_PREFIXES) or ext in ALLOWED_EXTENSIONS
    if not type_ok:
        return Response(
            {"detail": "Faqat rasm va video yuklash mumkin."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    limit = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if upload.size > limit:
        return Response(
            {"detail": f"Fayl juda katta. Chegara — {settings.MAX_UPLOAD_SIZE_MB} MB."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = (request.data.get("guest_code") or "").strip()
    guest = Guest.objects.filter(wedding=wedding, code__iexact=code).first() if code else None

    folder = f"{slugify(name)[:24] or 'mehmon'}-{guest.code if guest else 'x'}"
    already = GuestUpload.objects.filter(wedding=wedding, folder_name=folder).count()
    if already >= settings.MAX_UPLOADS_PER_GUEST:
        return Response(
            {"detail": f"Chegara: {settings.MAX_UPLOADS_PER_GUEST} ta fayl."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    obj = GuestUpload.objects.create(
        wedding=wedding,
        guest=guest,
        uploader_name=name,
        folder_name=folder,
        file=upload,
        original_name=os.path.basename(upload.name)[:255],
        content_type=ctype[:100],
        size=upload.size,
        caption=(request.data.get("caption") or "")[:200],
        is_video=ext in VIDEO_EXTENSIONS or ctype.startswith("video/"),
    )
    return Response(GuestUploadSerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@throttle_classes([RsvpThrottle])
def wish_create(request):
    """Mehmon tilagi. Darhol sahifada ko'rinadi, admin yashira oladi."""
    wedding = get_wedding()

    serializer = WishCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code = (request.data.get("guest_code") or "").strip()
    guest = Guest.objects.filter(wedding=wedding, code__iexact=code).first() if code else None

    wish = Wish.objects.create(
        wedding=wedding,
        guest=guest,
        is_visible=not wedding.wishes_need_approval,
        **serializer.validated_data,
    )
    data = WishSerializer(wish).data
    # Tasdiq kutayotgan tilak sahifada darhol ko'rinmaydi
    data["pending"] = not wish.is_visible
    return Response(data, status=status.HTTP_201_CREATED)


# ------------------------------------------------------- admin: ko'rish/yuklash


def _safe_open(upload: GuestUpload):
    path = Path(settings.PRIVATE_MEDIA_ROOT) / upload.file.name
    root = Path(settings.PRIVATE_MEDIA_ROOT).resolve()
    if not str(path.resolve()).startswith(str(root)) or not path.exists():
        raise Http404("Fayl topilmadi.")
    return path


@staff_member_required
def upload_serve(request, pk):
    """Faylni brauzerda ko'rsatish (admin uchun oldindan ko'rish)."""
    upload = get_object_or_404(GuestUpload, pk=pk)
    path = _safe_open(upload)
    ctype = upload.content_type or mimetypes.guess_type(upload.original_name)[0]
    return FileResponse(open(path, "rb"), content_type=ctype or "application/octet-stream")


@staff_member_required
def upload_download(request, pk):
    """Bitta faylni asl nomi bilan yuklab olish."""
    upload = get_object_or_404(GuestUpload, pk=pk)
    path = _safe_open(upload)
    return FileResponse(
        open(path, "rb"),
        as_attachment=True,
        filename=upload.original_name or path.name,
    )


def _build_zip(uploads, response_name):
    """Fayllarni papkalarga ajratib zip qiladi: <yuklovchi>/<fayl nomi>"""
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    used = set()
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        for up in uploads:
            src = Path(settings.PRIVATE_MEDIA_ROOT) / up.file.name
            if not src.exists():
                continue
            base = up.original_name or src.name
            arcname = f"{up.folder_name}/{base}"
            counter = 1
            while arcname in used:
                stem, ext = os.path.splitext(base)
                arcname = f"{up.folder_name}/{stem} ({counter}){ext}"
                counter += 1
            used.add(arcname)
            zf.write(src, arcname)
    tmp.close()

    response = FileResponse(
        open(tmp.name, "rb"), as_attachment=True, filename=response_name
    )
    response._resource_closers.append(lambda: os.unlink(tmp.name))
    return response


@staff_member_required
def download_folder(request, folder):
    uploads = GuestUpload.objects.filter(folder_name=folder)
    if not uploads.exists():
        raise Http404("Bu papkada fayl yo'q.")
    return _build_zip(uploads, f"{folder}.zip")


@staff_member_required
def download_all(request):
    uploads = GuestUpload.objects.all()
    if not uploads.exists():
        return HttpResponse("Hali hech kim fayl yuklamagan.", content_type="text/plain")
    stamp = timezone.localtime().strftime("%Y-%m-%d")
    return _build_zip(uploads, f"toy-esdaliklari-{stamp}.zip")


@staff_member_required
def uploads_browser(request):
    """Kim nima yuklaganini kartochka ko'rinishida ko'rsatadi."""
    folders = (
        GuestUpload.objects.values("folder_name", "uploader_name")
        .annotate(
            count=Count("id"),
            total=Sum("size"),
            first_at=Min("created_at"),
            last_at=Max("created_at"),
        )
        .order_by("-last_at")
    )

    cards = []
    for f in folders:
        items = GuestUpload.objects.filter(folder_name=f["folder_name"])
        cover = items.filter(is_video=False).order_by("created_at").first() or items.first()
        cards.append(
            {
                "folder": f["folder_name"],
                "name": f["uploader_name"],
                "count": f["count"],
                "photos": items.filter(is_video=False).count(),
                "videos": items.filter(is_video=True).count(),
                "size_mb": round((f["total"] or 0) / (1024 * 1024), 1),
                "first_at": f["first_at"],
                "last_at": f["last_at"],
                "cover": cover,
            }
        )

    total_size = GuestUpload.objects.aggregate(s=Sum("size"))["s"] or 0
    return render(
        request,
        "admin/uploads_browser.html",
        {
            "cards": cards,
            "total_files": GuestUpload.objects.count(),
            "total_people": len(cards),
            "total_size_mb": round(total_size / (1024 * 1024), 1),
            "title": "Mehmonlar yuklagan esdaliklar",
        },
    )


@staff_member_required
def uploads_folder(request, folder):
    """Bitta mehmon yuklagan fayllar — alohida sahifa."""
    items = GuestUpload.objects.filter(folder_name=folder).order_by("-created_at")
    if not items.exists():
        raise Http404("Bu papkada fayl yo'q.")

    total = items.aggregate(s=Sum("size"))["s"] or 0
    first = items.last()
    return render(
        request,
        "admin/uploads_folder.html",
        {
            "folder": folder,
            "name": first.uploader_name,
            "items": items,
            "count": items.count(),
            "size_mb": round(total / (1024 * 1024), 1),
            "first_at": first.created_at,
            "title": f"{first.uploader_name} yuklagan esdaliklar",
        },
    )
