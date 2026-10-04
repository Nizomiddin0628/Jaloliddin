"""Panel sahifalarining umumiy ma'lumoti: menyu, ruxsatlar, sanoqlar."""
from invitation.models import Wedding, Wish


def panel(request):
    if not request.path.startswith("/panel/") or not getattr(request, "user", None):
        return {}
    user = request.user
    if not user.is_authenticated or not user.is_staff:
        return {}

    def can(perm):
        return user.has_perm(f"invitation.{perm}")

    nav = [
        ("home", "panel:home", "Bosh sahifa", "home", True),
        ("guests", "panel:guests", "Mehmonlar", "users", can("view_guest")),
        ("rsvps", "panel:rsvps", "Javoblar", "reply", can("view_rsvp")),
        ("wishes", "panel:wishes", "Tilaklar", "heart", can("view_wish")),
        ("wedding", "panel:wedding", "To'y ma'lumotlari", "ring", can("view_wedding")),
        ("labels", "panel:labels", "Sahifa yozuvlari", "text", can("view_wedding")),
        ("gallery", "panel:gallery", "Galereya", "photo", can("view_galleryphoto")),
        ("timeline", "panel:timeline", "Sevgi tarixi", "thread", can("view_timelineevent")),
        ("duas", "panel:duas", "Duolar", "book", can("view_dua")),
        ("uploads", "panel:uploads", "Esdaliklar", "upload", can("view_guestupload")),
    ]
    return {
        "panel_nav": [
            {"key": k, "url": u, "label": l, "icon": i} for k, u, l, i, ok in nav if ok
        ],
        "panel_pending": Wish.objects.filter(is_visible=False).count() if can("view_wish") else 0,
        "panel_wedding": Wedding.objects.filter(is_active=True).first() or Wedding.objects.first(),
    }
