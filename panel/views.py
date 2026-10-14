"""
Boshqaruv paneli — /panel/
Django admin'ning o'rniga oddiy sayt ko'rinishidagi panel. Telefon va
kompyuterda qulay. Django admin /admin/ da zaxira sifatida qoladi.
"""
import base64
import csv
import io
import json
import os
import tempfile
import zipfile
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Count, Max, Prefetch, Q, Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from invitation import i18n
from invitation.models import Dua, GalleryPhoto, Guest, GuestUpload, Wedding, Wish

from .forms import BulkGuestForm, DuaForm, GalleryCaptionForm, GuestForm, WeddingForm

# ------------------------------------------------------------------ yordamchilar


def panel_view(perm=None):
    """
    Faqat xodim (is_staff) kiradi. `perm` berilsa — o'sha ruxsat ham kerak,
    masalan "change_wedding". Super admin hammasiga kiradi.
    """

    def deco(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated or not user.is_staff:
                return redirect(f"{reverse('panel:login')}?next={request.get_full_path()}")
            if perm and not user.has_perm(f"invitation.{perm}"):
                return render(request, "panel/denied.html", status=403)
            return fn(request, *args, **kwargs)

        return wrapper

    return deco


def is_ajax(request):
    return request.headers.get("x-requested-with") == "fetch"


def allowed_weddings(user):
    """
    Foydalanuvchi qaysi to'ylarni boshqaradi. Super admin — hammasini,
    qolganlar faqat o'ziga biriktirilganini. Hech biriga biriktirilmagan
    xodim esa hech narsa ko'rmaydi — boshqa tomonning mehmonlari,
    javoblari va rasmlari unga ochilmaydi.
    """
    if not user.is_authenticated:
        return Wedding.objects.none()
    if user.is_superuser:
        return Wedding.objects.all()
    return Wedding.objects.filter(editors=user)


def current_wedding(request):
    """
    Panelda hozir ochiq turgan to'y. Yuqoridagi almashtirgichdan tanlanadi
    (?toy=kelin) va seansda eslab qolinadi, shunda har sahifada qayta
    tanlash shart emas.
    """
    qs = allowed_weddings(request.user)
    slug = (request.GET.get("toy") or request.session.get("panel_toy") or "").strip()
    w = qs.filter(slug=slug).first() if slug else None
    if w is None:
        w = qs.first()
    if w is not None and request.session.get("panel_toy") != w.slug:
        request.session["panel_toy"] = w.slug
    return w


def need_wedding(request):
    w = current_wedding(request)
    if not w:
        messages.info(request, "Avval to'y ma'lumotlarini kiriting.")
    return w


def only(model, request, **kw):
    """Shu to'yga tegishli yozuvlar. Hamma so'rov shundan o'tadi."""
    return model.objects.filter(wedding=current_wedding(request), **kw)


def qr_png(text, box=10):
    try:
        import qrcode
    except ImportError:
        return None
    buf = io.BytesIO()
    qr = qrcode.QRCode(box_size=box, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(text)
    qr.make(fit=True)
    qr.make_image(fill_color="#15244a", back_color="white").save(buf, format="PNG")
    return buf.getvalue()


def renumber(qs):
    """Tartib raqamlarini 0, 1, 2… qilib tekislaydi."""
    for i, obj in enumerate(qs):
        if obj.order != i:
            type(obj).objects.filter(pk=obj.pk).update(order=i)


def move(model, pk, direction, **scope):
    items = list(model.objects.filter(**scope).order_by("order", "id"))
    idx = next((i for i, o in enumerate(items) if o.pk == pk), None)
    if idx is None:
        raise Http404
    j = idx + (-1 if direction == "up" else 1)
    if 0 <= j < len(items):
        items[idx], items[j] = items[j], items[idx]
    renumber(items)


def guest_status(guest):
    """Mehmon kartasidagi holat yozuvi — havolani ochgan-ochmagani."""
    if guest.open_count:
        return "opened", f"Ochgan · {guest.open_count} marta"
    return "unseen", "Hali ochmagan"


def back(request, fallback):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, {request.get_host()}):
        return redirect(nxt)
    return redirect(fallback)


# ------------------------------------------------------------------ kirish


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("panel:home")

    error = ""
    username = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        user = authenticate(request, username=username, password=request.POST.get("password", ""))
        if user is None:
            error = "Login yoki parol noto'g'ri."
        elif not user.is_staff:
            error = "Bu hisobga boshqaruv paneliga kirish ruxsati berilmagan."
        else:
            login(request, user)
            nxt = request.GET.get("next", "")
            if nxt and url_has_allowed_host_and_scheme(nxt, {request.get_host()}):
                return redirect(nxt)
            return redirect("panel:home")

    return render(request, "panel/login.html", {"error": error, "username": username,
         "w": Wedding.objects.filter(is_default=True).first() or Wedding.objects.first()})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("panel:login")


# ------------------------------------------------------------------ bosh sahifa


@panel_view()
def home(request):
    w = current_wedding(request)
    guests = Guest.objects.filter(wedding=w)
    wishes = Wish.objects.filter(wedding=w)
    uploads = GuestUpload.objects.filter(wedding=w)

    total_guests = guests.count()
    opened = guests.filter(open_count__gt=0).count()
    not_opened = max(total_guests - opened, 0)

    # Donut: taklifnomani kim ochgan. Aylana uzunligi 100 deb olinadi.
    parts_total = total_guests or 1
    donut = []
    offset = 25
    for key, count in (("yes", opened), ("wait", not_opened)):
        share = round(count * 100 / parts_total, 2)
        donut.append({"key": key, "share": share, "gap": round(100 - share, 2), "offset": offset})
        offset = (offset - share) % 100

    # So'nggi voqealar
    feed = []
    for x in wishes.order_by("-created_at")[:8]:
        feed.append({
            "at": x.created_at, "kind": "wish",
            "text": f"{x.name} tilak qoldirdi" + ("" if x.is_visible else " · tasdiq kutmoqda"),
        })
    for g in guests.filter(opened_at__isnull=False).order_by("-opened_at")[:8]:
        feed.append({"at": g.opened_at, "kind": "open", "text": f"{g.display_name} taklifnomani ochdi"})
    for u in (uploads.values("uploader_name").annotate(n=Count("id"), at=Max("created_at"))
              .order_by("-at")[:4]):
        feed.append({"at": u["at"], "kind": "upload", "text": f"{u['uploader_name']} {u['n']} ta fayl yukladi"})
    feed.sort(key=lambda x: x["at"], reverse=True)

    days_left = None
    if w:
        days_left = (timezone.localtime(w.event_at).date() - timezone.localdate()).days

    return render(request, "panel/home.html", {
        "w": w,
        "nav": "home",
        "days_left": days_left,
        "st": {
            "guests": total_guests,
            "opened": opened,
            "not_opened": not_opened,
            "opened_pct": round(opened * 100 / total_guests) if total_guests else 0,
            "wishes": wishes.count(),
            "wishes_pending": wishes.filter(is_visible=False).count(),
            "uploads": uploads.count(),
        },
        "donut": donut,
        "feed": feed[:12],
    })


@panel_view("change_wedding")
@require_POST
def toggle(request):
    """Bosh sahifadagi almashtirgichlar. JSON qaytaradi."""
    w = current_wedding(request)
    if not w:
        return JsonResponse({"ok": False, "detail": "To'y topilmadi."}, status=404)
    try:
        data = json.loads(request.body or "{}")
    except ValueError:
        data = request.POST
    field = data.get("field")
    allowed = {"uploads_open", "wishes_need_approval", "show_english"}
    if field in allowed:
        setattr(w, field, bool(data.get("value")))
    elif field == "mode" and data.get("value") in (Wedding.MODE_INVITATION, Wedding.MODE_THANKS):
        w.mode = data["value"]
    else:
        return JsonResponse({"ok": False, "detail": "Noma'lum sozlama."}, status=400)
    Wedding.objects.filter(pk=w.pk).update(**{field: getattr(w, field)}, updated_at=timezone.now())
    return JsonResponse({"ok": True, "field": field, "value": getattr(w, field)})


# ------------------------------------------------------------------ to'y ma'lumotlari


@panel_view("view_wedding")
def wedding_edit(request):
    w = current_wedding(request)
    if w is None and not request.user.has_perm("invitation.add_wedding"):
        return render(request, "panel/denied.html", status=403)
    can_edit = request.user.has_perm("invitation.change_wedding" if w else "invitation.add_wedding")

    if request.method == "POST" and can_edit:
        form = WeddingForm(request.POST, request.FILES, instance=w)
        if form.is_valid():
            obj = form.save()
            for name in ("hero_image", "music"):
                if request.POST.get(f"{name}-clear") and getattr(obj, name):
                    getattr(obj, name).delete(save=True)
            messages.success(request, "Saqlandi. Saytda darhol ko'rinadi.")
            return redirect(f"{reverse('panel:wedding')}?tab={request.POST.get('tab', 'asosiy')}")
        messages.error(request, "Ba'zi maydonlarda xato bor — qizil bilan belgilangan.")
    else:
        form = WeddingForm(instance=w)

    return render(request, "panel/wedding.html", {
        "w": w, "form": form, "nav": "wedding", "can_edit": can_edit,
        "tab": request.GET.get("tab", "asosiy"),
    })


# ------------------------------------------------------------------ sahifa yozuvlari


@panel_view("view_wedding")
def labels(request):
    """Bo'lim sarlavhalari va tugma yozuvlarini o'zgartirish."""
    w = current_wedding(request)
    if not w:
        messages.info(request, "Avval to'y ma'lumotlarini kiriting.")
        return redirect("panel:wedding")
    can_edit = request.user.has_perm("invitation.change_wedding")
    current = w.labels if isinstance(w.labels, dict) else {}

    if request.method == "POST" and can_edit:
        if request.POST.get("reset"):
            new = {}
        else:
            new = {"uz": {}, "en": {}}
            for lang in ("uz", "en"):
                for key in i18n.EDITABLE_KEYS:
                    val = request.POST.get(f"{lang}__{key}", "").strip()[:300]
                    # Standart matn bilan bir xil bo'lsa saqlamaymiz
                    if val and val != i18n.UI[lang].get(key, ""):
                        new[lang][key] = val

        # Bo'lim yoqib-o'chirgichlari shu formaning o'zida saqlanadi
        switches = {
            field: request.POST.get(f"on__{field}") == "1"
            for field in i18n.SECTION_FIELDS
        }
        Wedding.objects.filter(pk=w.pk).update(
            labels=new, updated_at=timezone.now(), **switches
        )
        messages.success(request, "Saqlandi. Saytda darhol ko'rinadi.")
        return redirect("panel:labels")

    groups = []
    for field, title, note, items in i18n.SECTIONS:
        rows = []
        for key, hint in items:
            rows.append({
                "key": key,
                "hint": hint,
                "uz": (current.get("uz") or {}).get(key, ""),
                "en": (current.get("en") or {}).get(key, ""),
                "uz_default": i18n.UI["uz"].get(key, ""),
                "en_default": i18n.UI["en"].get(key, ""),
            })
        groups.append({
            "title": title,
            "note": note,
            "field": field,
            "on": getattr(w, field) if field else None,
            "rows": rows,
        })
    changed = sum(len(v) for v in current.values() if isinstance(v, dict))
    off = sum(1 for g in groups if g["field"] and not g["on"])
    return render(request, "panel/labels.html", {
        "nav": "labels", "groups": groups, "can_edit": can_edit,
        "changed": changed, "off": off,
    })


# ------------------------------------------------------------------ mehmonlar


@panel_view("view_guest")
def guests(request):
    w = current_wedding(request)
    q = request.GET.get("q", "").strip()
    f = request.GET.get("f", "all")

    qs = Guest.objects.filter(wedding=w).order_by("-created_at")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(note__icontains=q) | Q(code__icontains=q))

    rows = []
    counts = {"all": 0, "opened": 0, "unseen": 0}
    for g in qs:
        key, label = guest_status(g)
        counts["all"] += 1
        counts[key] += 1
        if f == "all" or f == key:
            rows.append({"g": g, "status": key, "label": label})

    return render(request, "panel/guests.html", {
        "w": w, "nav": "guests", "rows": rows, "q": q, "f": f, "counts": counts,
        "form": GuestForm(), "bulk": BulkGuestForm(),
        "filters": [("all", "Hammasi"), ("opened", "Ochgan"), ("unseen", "Ochmagan")],
    })


@panel_view("add_guest")
@require_POST
def guest_add(request):
    w = need_wedding(request)
    if not w:
        return redirect("panel:wedding")
    form = GuestForm(request.POST, request.FILES)
    if form.is_valid():
        g = form.save(commit=False)
        g.wedding = w
        g.save()
        messages.success(request, f"{g.display_name} qo'shildi. Havolasini nusxalab yuborishingiz mumkin.")
    else:
        messages.error(request, "Mehmon ismini yozing.")
    return redirect("panel:guests")


@panel_view("add_guest")
@require_POST
def guest_bulk(request):
    w = need_wedding(request)
    if not w:
        return redirect("panel:wedding")
    form = BulkGuestForm(request.POST)
    if form.is_valid():
        items = form.parse()
        with transaction.atomic():
            for it in items:
                Guest(wedding=w, **it).save()
        messages.success(request, f"{len(items)} ta mehmon qo'shildi.")
    else:
        messages.error(request, "Ro'yxat bo'sh.")
    return redirect("panel:guests")


@panel_view("view_guest")
def guest_edit(request, pk):
    g = get_object_or_404(Guest, pk=pk, wedding=current_wedding(request))
    can_edit = request.user.has_perm("invitation.change_guest")
    if request.method == "POST" and can_edit:
        form = GuestForm(request.POST, request.FILES, instance=g)
        if form.is_valid():
            obj = form.save()
            for name in ("hero_image", "music"):
                if request.POST.get(f"{name}-clear") and getattr(obj, name):
                    getattr(obj, name).delete(save=True)
            messages.success(request, "Saqlandi.")
            return redirect("panel:guests")
    else:
        form = GuestForm(instance=g)
    key, label = guest_status(g)
    qr = qr_png(g.invite_url, box=8)
    return render(request, "panel/guest_edit.html", {
        "g": g, "form": form, "nav": "guests", "can_edit": can_edit,
        "status": key, "status_label": label,
        "qr": "data:image/png;base64," + base64.b64encode(qr).decode() if qr else "",
    })


@panel_view("delete_guest")
@require_POST
def guest_delete(request, pk):
    g = get_object_or_404(Guest, pk=pk, wedding=current_wedding(request))
    name = g.display_name
    g.delete()
    if is_ajax(request):
        return JsonResponse({"ok": True})
    messages.success(request, f"{name} o'chirildi.")
    return redirect("panel:guests")


@panel_view("view_guest")
def guest_qr(request, pk):
    g = get_object_or_404(Guest, pk=pk, wedding=current_wedding(request))
    png = qr_png(g.invite_url, box=14)
    if png is None:
        raise Http404("qrcode o'rnatilmagan")
    resp = HttpResponse(png, content_type="image/png")
    if request.GET.get("download"):
        resp["Content-Disposition"] = f'attachment; filename="qr-{g.code}.png"'
    return resp


@panel_view("view_guest")
def guests_csv(request):
    resp = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    resp["Content-Disposition"] = 'attachment; filename="mehmonlar.csv"'
    wr = csv.writer(resp)
    wr.writerow(["Ism", "Murojaat", "Kishi", "Izoh", "Havola", "Necha marta ochgan"])
    for g in Guest.objects.filter(wedding=current_wedding(request)).order_by("name"):
        wr.writerow([g.name, g.honorific, g.seats, g.note, g.invite_url, g.open_count])
    return resp


@panel_view("view_guest")
def guests_qr_zip(request):
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with zipfile.ZipFile(tmp, "w") as zf:
        for g in Guest.objects.filter(wedding=current_wedding(request)):
            png = qr_png(g.invite_url, box=12)
            if png:
                zf.writestr(f"{g.code}__{g.name}.png", png)
    tmp.close()
    resp = FileResponse(open(tmp.name, "rb"), as_attachment=True, filename="qr-kodlar.zip")
    resp._resource_closers.append(lambda: os.unlink(tmp.name))
    return resp


# ------------------------------------------------------------------ tilaklar


@panel_view("view_wish")
def wishes(request):
    f = request.GET.get("f", "wait")
    base = Wish.objects.filter(wedding=current_wedding(request)).order_by("-created_at")
    counts = {
        "wait": base.filter(is_visible=False).count(),
        "shown": base.filter(is_visible=True).count(),
        "all": base.count(),
    }
    if f == "wait" and counts["wait"] == 0 and "f" not in request.GET:
        f = "all"
    qs = {"wait": base.filter(is_visible=False), "shown": base.filter(is_visible=True)}.get(f, base)
    w = current_wedding(request)
    return render(request, "panel/wishes.html", {
        "nav": "wishes", "items": qs, "f": f, "counts": counts, "w": w,
        "filters": [("wait", "Tasdiq kutmoqda"), ("shown", "Sahifada"), ("all", "Hammasi")],
    })


@panel_view("view_wish")
@require_POST
def wish_action(request, pk):
    x = get_object_or_404(Wish, pk=pk, wedding=current_wedding(request))
    act = request.POST.get("act")
    user = request.user
    if act in ("show", "hide") and user.has_perm("invitation.change_wish"):
        x.is_visible = act == "show"
        x.save(update_fields=["is_visible"])
        msg = "Tilak sahifaga chiqdi." if x.is_visible else "Tilak yashirildi."
    elif act == "delete" and user.has_perm("invitation.delete_wish"):
        x.delete()
        msg = "Tilak o'chirildi."
    else:
        return JsonResponse({"ok": False, "detail": "Ruxsat yo'q."}, status=403)
    if is_ajax(request):
        pending = Wish.objects.filter(wedding=current_wedding(request), is_visible=False).count()
        return JsonResponse({"ok": True, "msg": msg, "pending": pending})
    messages.success(request, msg)
    return back(request, "panel:wishes")


@panel_view("change_wish")
@require_POST
def wishes_approve_all(request):
    n = Wish.objects.filter(wedding=current_wedding(request), is_visible=False).update(is_visible=True)
    messages.success(request, f"{n} ta tilak sahifaga chiqdi.")
    return redirect("panel:wishes")


# ------------------------------------------------------------------ galereya


@panel_view("view_galleryphoto")
def gallery(request):
    w = current_wedding(request)
    if request.method == "POST":
        if not request.user.has_perm("invitation.add_galleryphoto"):
            return render(request, "panel/denied.html", status=403)
        if not w:
            return redirect("panel:wedding")
        files = request.FILES.getlist("images")
        start = (GalleryPhoto.objects.filter(wedding=w).aggregate(m=Max("order"))["m"] or 0) + 1
        added = 0
        for i, f in enumerate(files):
            if not (f.content_type or "").startswith("image/"):
                continue
            p = GalleryPhoto(wedding=w, image=f, order=start + i)
            p.save()
            added += 1
        if is_ajax(request):
            return JsonResponse({"ok": True, "added": added})
        messages.success(request, f"{added} ta rasm qo'shildi." if added else "Rasm tanlanmadi.")
        return redirect("panel:gallery")

    photos = GalleryPhoto.objects.filter(wedding=w).order_by("order", "id") if w else []
    return render(request, "panel/gallery.html", {"nav": "gallery", "photos": photos, "w": w})


@panel_view("change_galleryphoto")
@require_POST
def gallery_item(request, pk):
    p = get_object_or_404(GalleryPhoto, pk=pk, wedding=current_wedding(request))
    act = request.POST.get("act")
    if act in ("up", "down"):
        move(GalleryPhoto, p.pk, act, wedding=p.wedding)
    elif act == "caption":
        form = GalleryCaptionForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
    elif act == "delete" and request.user.has_perm("invitation.delete_galleryphoto"):
        p.image.delete(save=False)
        p.delete()
        messages.success(request, "Rasm o'chirildi.")
    elif act == "order":
        # Sudrab tartiblash: id'lar ro'yxati keladi
        ids = [int(x) for x in request.POST.get("ids", "").split(",") if x.isdigit()]
        for i, pid in enumerate(ids):
            GalleryPhoto.objects.filter(pk=pid, wedding=p.wedding).update(order=i)
    if is_ajax(request):
        return JsonResponse({"ok": True})
    return redirect("panel:gallery")


# ------------------------------------------------------------------ duolar


@panel_view("view_dua")
def duas(request):
    w = current_wedding(request)
    if request.method == "POST":
        if not w:
            return redirect("panel:wedding")
        pk = request.POST.get("pk")
        inst = get_object_or_404(Dua, pk=pk, wedding=w) if pk else None
        perm = "change_dua" if inst else "add_dua"
        if not request.user.has_perm(f"invitation.{perm}"):
            return render(request, "panel/denied.html", status=403)
        form = DuaForm(request.POST, instance=inst, prefix=f"d{pk}" if pk else None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.wedding = w
            if not inst:
                obj.order = (Dua.objects.filter(wedding=w).aggregate(m=Max("order"))["m"] or 0) + 1
            obj.save()
            messages.success(request, "Saqlandi.")
            return redirect("panel:duas")
        messages.error(request, "Sarlavha va ma'nosini yozing.")
    items = Dua.objects.filter(wedding=w).order_by("order", "id") if w else []
    return render(request, "panel/duas.html", {
        "nav": "duas",
        "items": [(d, DuaForm(instance=d, prefix=f"d{d.pk}")) for d in items],
        "form": DuaForm(initial={"is_visible": True}),
    })


@panel_view("change_dua")
@require_POST
def dua_item(request, pk):
    d = get_object_or_404(Dua, pk=pk)
    act = request.POST.get("act")
    if act in ("up", "down"):
        move(Dua, d.pk, act, wedding=d.wedding)
    elif act == "toggle":
        d.is_visible = not d.is_visible
        d.save(update_fields=["is_visible"])
    elif act == "delete" and request.user.has_perm("invitation.delete_dua"):
        d.delete()
        messages.success(request, "Duo o'chirildi.")
    return redirect("panel:duas")


# ------------------------------------------------------------------ esdaliklar


@panel_view("view_guestupload")
def uploads(request):
    w = current_wedding(request)
    folders = (
        GuestUpload.objects.filter(wedding=w).values("folder_name", "uploader_name")
        .annotate(count=Count("id"), total=Sum("size"), last_at=Max("created_at"),
                  videos=Count("id", filter=Q(is_video=True)))
        .order_by("-last_at")
    )
    cards = []
    for f in folders:
        items = GuestUpload.objects.filter(wedding=w, folder_name=f["folder_name"])
        cover = items.filter(is_video=False).order_by("created_at").first()
        cards.append({
            "folder": f["folder_name"], "name": f["uploader_name"], "count": f["count"],
            "videos": f["videos"], "photos": f["count"] - f["videos"],
            "size_mb": round((f["total"] or 0) / (1024 * 1024), 1),
            "last_at": f["last_at"], "cover": cover,
        })
    total = GuestUpload.objects.filter(wedding=w).aggregate(s=Sum("size"))["s"] or 0
    return render(request, "panel/uploads.html", {
        "nav": "uploads", "cards": cards, "w": w,
        "total_files": GuestUpload.objects.filter(wedding=w).count(),
        "total_mb": round(total / (1024 * 1024), 1),
    })


@panel_view("view_guestupload")
def uploads_folder(request, folder):
    items = GuestUpload.objects.filter(wedding=current_wedding(request), folder_name=folder).order_by("-created_at")
    if not items.exists():
        raise Http404
    total = items.aggregate(s=Sum("size"))["s"] or 0
    return render(request, "panel/uploads_folder.html", {
        "nav": "uploads", "folder": folder, "name": items.first().uploader_name,
        "items": items, "count": items.count(), "size_mb": round(total / (1024 * 1024), 1),
    })


@panel_view("delete_guestupload")
@require_POST
def upload_delete(request, pk):
    u = get_object_or_404(GuestUpload, pk=pk, wedding=current_wedding(request))
    folder = u.folder_name
    u.file.delete(save=False)
    u.delete()
    if is_ajax(request):
        return JsonResponse({"ok": True})
    messages.success(request, "Fayl o'chirildi.")
    if GuestUpload.objects.filter(wedding=current_wedding(request), folder_name=folder).exists():
        return redirect("panel:uploads-folder", folder=folder)
    return redirect("panel:uploads")
