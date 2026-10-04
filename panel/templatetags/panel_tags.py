from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def oldin(value):
    """«5 daqiqa oldin», «kecha», «3 kun oldin» — o'zbekcha."""
    if not value:
        return ""
    sec = int((timezone.now() - value).total_seconds())
    if sec < 0:
        return "hozir"
    if sec < 60:
        return "hozirgina"
    if sec < 3600:
        return f"{sec // 60} daqiqa oldin"
    if sec < 86400:
        return f"{sec // 3600} soat oldin"
    days = sec // 86400
    if days == 1:
        return "kecha"
    if days < 30:
        return f"{days} kun oldin"
    return timezone.localtime(value).strftime("%d.%m.%Y")


@register.filter
def widget_kind(bound_field):
    w = bound_field.field.widget
    name = type(w).__name__
    if name == "CheckboxInput":
        return "switch"
    if name in ("ClearableFileInput", "FileInput"):
        return "file"
    if name == "Textarea":
        return "textarea"
    return "input"


@register.filter
def initials(name):
    parts = [p for p in str(name).split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


@register.simple_tag
def icon(name, size=20):
    from django.utils.html import format_html
    return format_html('<svg class="ic" width="{0}" height="{0}" aria-hidden="true"><use href="#p-{1}"/></svg>', size, name)
