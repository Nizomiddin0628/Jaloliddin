"""Boshqaruv panelining bosh sahifasi uchun qisqa statistika."""
from django import template

from invitation.models import Guest, GuestUpload, Rsvp, Wedding, Wish

register = template.Library()


@register.simple_tag
def wedding_stats():
    keladi = Rsvp.objects.filter(attending=True)
    wedding = Wedding.objects.filter(is_active=True).first()
    return {
        "wedding": wedding,
        "guests": Guest.objects.count(),
        "answered": Rsvp.objects.count(),
        "coming": keladi.count(),
        "people": sum(r.seats for r in keladi),
        "wishes": Wish.objects.filter(is_visible=True).count(),
        "wishes_pending": Wish.objects.filter(is_visible=False).count(),
        "uploads": GuestUpload.objects.count(),
        "uploaders": GuestUpload.objects.values("folder_name").distinct().count(),
    }