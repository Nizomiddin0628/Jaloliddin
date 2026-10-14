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
        ("wishes", "panel:wishes", "Tilaklar", "heart", can("view_wish")),
        ("wedding", "panel:wedding", "To'y ma'lumotlari", "ring", can("view_wedding")),
        ("labels", "panel:labels", "Sahifa yozuvlari", "text", can("view_wedding")),
        ("gallery", "panel:gallery", "Galereya", "photo", can("view_galleryphoto")),
        ("duas", "panel:duas", "Duolar", "book", can("view_dua")),
        ("uploads", "panel:uploads", "Esdaliklar", "upload", can("view_guestupload")),
    ]
    # Panelda hozir ochiq turgan to'y va foydalanuvchiga ruxsat etilganlari.
    # Almashtirgich faqat bir nechtasi bo'lganda ko'rinadi.
    from panel.views import allowed_weddings, current_wedding

    mine = list(allowed_weddings(user))
    current = current_wedding(request)

    return {
        "panel_nav": [
            {"key": k, "url": u, "label": l, "icon": i} for k, u, l, i, ok in nav if ok
        ],
        "panel_pending": (
            Wish.objects.filter(wedding=current, is_visible=False).count()
            if can("view_wish") and current else 0
        ),
        "panel_wedding": current,
        "panel_weddings": mine,
    }
