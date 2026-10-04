from django import forms

from invitation.models import Dua, GalleryPhoto, Guest, TimelineEvent, Wedding


class DateTimeLocal(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%dT%H:%M", **kwargs)


class WeddingForm(forms.ModelForm):
    """To'y ma'lumotlari. Bo'limlarga bo'lish shablonda — `SECTIONS` bo'yicha."""

    SECTIONS = [
        ("asosiy", "Asosiy", [
            "groom_name", "bride_name", "event_at", "welcome_time",
            "venue_name", "venue_address", "map_url", "latitude", "longitude",
        ]),
        ("matn", "Matnlar", ["invite_text", "dress_code"]),
        ("media", "Rasm va musiqa", ["hero_image", "music"]),
        ("aloqa", "Aloqa", [
            "contact_one_name", "contact_one_phone", "contact_two_name", "contact_two_phone",
        ]),
        ("keyin", "To'ydan keyin", ["thanks_title", "thanks_text", "upload_hint"]),
        ("en", "Inglizcha", [
            "groom_name_en", "bride_name_en", "venue_name_en", "venue_address_en",
            "invite_text_en", "dress_code_en", "thanks_title_en", "thanks_text_en",
            "upload_hint_en",
        ]),
    ]

    class Meta:
        model = Wedding
        exclude = [
            "is_active", "mode", "rsvp_open", "uploads_open",
            "wishes_need_approval", "show_english", "updated_at", "labels",
        ]
        widgets = {
            "event_at": DateTimeLocal(),
            "invite_text": forms.Textarea(attrs={"rows": 4}),
            "invite_text_en": forms.Textarea(attrs={"rows": 4}),
            "thanks_text": forms.Textarea(attrs={"rows": 3}),
            "thanks_text_en": forms.Textarea(attrs={"rows": 3}),
            "upload_hint": forms.Textarea(attrs={"rows": 3}),
            "upload_hint_en": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "latitude": "Google Maps'da joyni toping, nuqtaga o'ng tugmani bosing — birinchi raqam.",
            "longitude": "O'sha joydagi ikkinchi raqam.",
            "map_url": "Ixtiyoriy. Yandex yoki Google Maps havolasi — «Yo'nalish» tugmasi shu yerga olib boradi.",
            "hero_image": "Telefondan yuklasangiz ham bo'ladi — sayt o'zi kichraytiradi.",
            "music": "MP3 fayl. Mehmon eshikni ochganda yangraydi.",
            "invite_text": "Mehmon eshikni ochgandan keyin o'qiydigan asosiy matn.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        for name in ("latitude", "longitude"):
            self.fields[name].widget.attrs.update({"step": "any", "inputmode": "decimal"})
        self.fields["hero_image"].widget.attrs["accept"] = "image/*"
        self.fields["music"].widget.attrs["accept"] = "audio/*"

    def sections(self):
        for key, title, names in self.SECTIONS:
            yield {
                "key": key,
                "title": title,
                "fields": [self[n] for n in names],
                "has_errors": any(self[n].errors for n in names),
            }


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ["name", "honorific", "seats", "note", "hero_image", "music"]
        help_texts = {
            "honorific": "aka, opa, xola, oila… Sahifada «Hurmatli Akmal aka» bo'lib chiqadi.",
            "seats": "Javob formasida shu son tayyor turadi.",
            "note": "Faqat sizga ko'rinadi. Masalan: kuyov tomondan, ishxonadan.",
            "hero_image": "Ixtiyoriy. Shu mehmonga alohida bosh rasm.",
            "music": "Ixtiyoriy. Shu mehmonga alohida musiqa.",
        }
        widgets = {"seats": forms.NumberInput(attrs={"min": 1, "max": 20})}


class BulkGuestForm(forms.Form):
    lines = forms.CharField(
        label="Mehmonlar ro'yxati",
        widget=forms.Textarea(attrs={
            "rows": 6,
            "placeholder": "Akmal, aka, 2\nZuhra, opa, 4\nKarimovlar, oila, 5\nBekzod",
        }),
        help_text="Har qatorga bitta mehmon: ism, murojaat, kishi soni. Faqat ism yozsangiz ham bo'ladi.",
    )

    def parse(self):
        out = []
        for raw in self.cleaned_data["lines"].splitlines():
            parts = [p.strip() for p in raw.replace(";", ",").replace("\t", ",").split(",")]
            parts = [p for p in parts if p]
            if not parts:
                continue
            name, honorific, seats = parts[0], "", 2
            for p in parts[1:]:
                if p.isdigit():
                    seats = max(1, min(20, int(p)))
                elif not honorific:
                    honorific = p[:40]
            out.append({"name": name[:120], "honorific": honorific, "seats": seats})
        return out


class TimelineForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        fields = ["date_label", "title", "text", "date_label_en", "title_en", "text_en"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
            "text_en": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {"date_label": "Erkin yozing: «2023-yil, kuz» yoki «Bahor»."}


class GalleryCaptionForm(forms.ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = ["caption"]


class DuaForm(forms.ModelForm):
    class Meta:
        model = Dua
        fields = ["title", "arabic", "transliteration", "meaning", "source",
                  "is_visible", "title_en", "meaning_en"]
        widgets = {
            "arabic": forms.Textarea(attrs={"rows": 3, "dir": "rtl", "lang": "ar"}),
            "transliteration": forms.Textarea(attrs={"rows": 3}),
            "meaning": forms.Textarea(attrs={"rows": 3}),
            "meaning_en": forms.Textarea(attrs={"rows": 3}),
        }
