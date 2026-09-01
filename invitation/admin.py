import csv
import io
import os
import tempfile
import zipfile

from django.conf import settings
from django.contrib import admin, messages
from django.http import FileResponse, HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import GalleryPhoto, Guest, GuestUpload, Rsvp, TimelineEvent, Wedding


class TimelineInline(admin.TabularInline):
    model = TimelineEvent
    extra = 1
    fields = ["order", "date_label", "title", "text"]


class GalleryInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 1
    fields = ["order", "image", "preview", "caption"]
    readonly_fields = ["preview"]

    @admin.display(description="Ko'rinishi")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:70px;border-radius:3px" />', obj.image.url
            )
        return "—"


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    inlines = [TimelineInline, GalleryInline]
    list_display = ["__str__", "event_at", "mode", "rsvp_open", "uploads_open"]
    save_on_top = True
    fieldsets = (
        ("Sahifa holati", {
            "fields": ("is_active", "mode", "rsvp_open", "uploads_open"),
            "description": (
                "To'y o'tgandan keyin rejimni «Rahmat sahifasi»ga o'tkazing va "
                "«Rasm yuklash ochiq» belgisini qo'ying — mehmonlar o'sha havolaga "
                "o'z rasmlarini yuklay boshlaydi."
            ),
        }),
        ("Kuyov va kelin", {"fields": ("groom_name", "bride_name", "hero_image", "music")}),
        ("Vaqt va joy", {
            "fields": ("event_at", "welcome_time", "venue_name", "venue_address",
                       "map_url", "latitude", "longitude")
        }),
        ("Matnlar", {"fields": ("invite_text", "dress_code")}),
        ("Aloqa", {
            "fields": ("contact_one_name", "contact_one_phone",
                       "contact_two_name", "contact_two_phone")
        }),
        ("To'ydan keyin", {"fields": ("thanks_title", "thanks_text", "upload_hint")}),
    )


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ["display_name", "seats", "link_column", "open_count", "answer"]
    list_filter = ["seats", "opened_at"]
    search_fields = ["name", "code", "note"]
    readonly_fields = ["code", "open_count", "opened_at", "qr_preview"]
    actions = ["export_links_csv", "download_qr_zip"]
    fields = ["wedding", "name", "honorific", "seats", "note", "code",
              "qr_preview", "open_count", "opened_at"]

    @admin.display(description="Shaxsiy havola")
    def link_column(self, obj):
        return format_html(
            '<a href="{0}" target="_blank" rel="noopener">{0}</a>', obj.invite_url
        )

    @admin.display(description="Javobi")
    def answer(self, obj):
        rsvp = obj.rsvps.first()
        if not rsvp:
            return format_html('<span style="color:#999">javob yo\'q</span>')
        if rsvp.attending:
            return format_html(
                '<b style="color:#2d6a2d">keladi · {} kishi</b>', rsvp.seats
            )
        return format_html('<span style="color:#a33">kelolmaydi</span>')

    @admin.display(description="QR kod")
    def qr_preview(self, obj):
        if not obj.pk:
            return "Avval saqlang."
        img = _qr_data_uri(obj.invite_url)
        if not img:
            return "qrcode kutubxonasi o'rnatilmagan."
        return mark_safe(
            f'<img src="{img}" style="width:190px" /><br>'
            f'<small>Qog\'oz taklifnoma orqasiga shuni bosasiz.</small>'
        )

    @admin.action(description="Tanlanganlarning havolalarini CSV qilib olish")
    def export_links_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="mehmon-havolalari.csv"'
        writer = csv.writer(response)
        writer.writerow(["Ism", "Murojaat", "Kishi", "Havola"])
        for g in queryset:
            writer.writerow([g.name, g.honorific, g.seats, g.invite_url])
        return response

    @admin.action(description="Tanlanganlarning QR kodlarini ZIP qilib olish")
    def download_qr_zip(self, request, queryset):
        try:
            import qrcode
        except ImportError:
            self.message_user(
                request, "qrcode kutubxonasi o'rnatilmagan: pip install qrcode",
                level=messages.ERROR,
            )
            return None

        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        with zipfile.ZipFile(tmp, "w") as zf:
            for g in queryset:
                buf = io.BytesIO()
                qrcode.make(g.invite_url, box_size=12, border=2).save(buf, format="PNG")
                zf.writestr(f"{g.code}__{g.name}.png", buf.getvalue())
        tmp.close()
        response = FileResponse(
            open(tmp.name, "rb"), as_attachment=True, filename="qr-kodlar.zip"
        )
        response._resource_closers.append(lambda: os.unlink(tmp.name))
        return response


def _qr_data_uri(text):
    try:
        import base64

        import qrcode
    except ImportError:
        return None
    buf = io.BytesIO()
    qrcode.make(text, box_size=8, border=2).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@admin.register(Rsvp)
class RsvpAdmin(admin.ModelAdmin):
    list_display = ["name", "attending", "seats", "phone", "short_message", "created_at"]
    list_filter = ["attending", "created_at"]
    search_fields = ["name", "phone", "message"]
    readonly_fields = ["created_at"]
    actions = ["export_csv"]

    @admin.display(description="Tilak")
    def short_message(self, obj):
        return (obj.message[:60] + "…") if len(obj.message) > 60 else obj.message

    @admin.action(description="Ro'yxatni CSV qilib olish (Excel uchun)")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="mehmonlar-royxati.csv"'
        writer = csv.writer(response)
        writer.writerow(["Ism", "Keladimi", "Kishi soni", "Telefon", "Tilak", "Sana"])
        for r in queryset:
            writer.writerow([
                r.name, "Ha" if r.attending else "Yo'q", r.seats, r.phone,
                r.message, r.created_at.strftime("%Y-%m-%d %H:%M"),
            ])
        return response

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        keladi = qs.filter(attending=True)
        extra_context = extra_context or {}
        extra_context["title"] = (
            f"Javoblar — {keladi.count()} ta oila keladi, "
            f"jami {sum(r.seats for r in keladi)} kishi"
        )
        return super().changelist_view(request, extra_context)


@admin.register(GuestUpload)
class GuestUploadAdmin(admin.ModelAdmin):
    list_display = ["thumb", "original_name", "uploader_name", "folder_name",
                    "kind", "size_column", "created_at", "actions_column"]
    list_filter = ["is_video", "created_at", "uploader_name"]
    search_fields = ["uploader_name", "original_name", "caption"]
    readonly_fields = ["uploader_name", "folder_name", "original_name", "content_type",
                       "size", "is_video", "created_at", "big_preview"]
    actions = ["download_selected_zip"]
    list_per_page = 40

    def has_add_permission(self, request):
        return False

    @admin.display(description="")
    def thumb(self, obj):
        url = reverse("upload-serve", args=[obj.pk])
        if obj.is_video:
            return format_html('<div style="font-size:24px">▶</div>')
        return format_html(
            '<img src="{}" style="height:56px;width:56px;object-fit:cover;'
            'border-radius:3px" loading="lazy" />', url
        )

    @admin.display(description="Katta ko'rinish")
    def big_preview(self, obj):
        url = reverse("upload-serve", args=[obj.pk])
        if obj.is_video:
            return format_html(
                '<video src="{}" controls style="max-width:520px"></video>', url
            )
        return format_html('<img src="{}" style="max-width:520px" />', url)

    @admin.display(description="Turi")
    def kind(self, obj):
        return "Video" if obj.is_video else "Rasm"

    @admin.display(description="Hajmi", ordering="size")
    def size_column(self, obj):
        return f"{obj.size_mb} MB"

    @admin.display(description="Amallar")
    def actions_column(self, obj):
        return format_html(
            '<a href="{}">Yuklab olish</a>',
            reverse("upload-download", args=[obj.pk]),
        )

    @admin.action(description="Tanlanganlarni ZIP qilib yuklab olish")
    def download_selected_zip(self, request, queryset):
        from .views import _build_zip

        return _build_zip(queryset, "tanlangan-esdaliklar.zip")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["browser_url"] = reverse("uploads-browser")
        extra_context["download_all_url"] = reverse("uploads-download-all")
        return super().changelist_view(request, extra_context)
