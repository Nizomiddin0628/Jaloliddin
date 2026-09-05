import os
import secrets
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Mehmonlar yuklagan fayllar shu saqlagichga tushadi.
# U MEDIA_ROOT'dan tashqarida, shuning uchun havolasini bilgan odam ham ocholmaydi.
private_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


def _rand_code(length=8):
    alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def gallery_path(instance, filename):
    return f"gallery/{uuid.uuid4().hex[:12]}{os.path.splitext(filename)[1].lower()}"


def hero_path(instance, filename):
    return f"hero/{uuid.uuid4().hex[:12]}{os.path.splitext(filename)[1].lower()}"


def music_path(instance, filename):
    return f"music/{uuid.uuid4().hex[:12]}{os.path.splitext(filename)[1].lower()}"


def guest_upload_path(instance, filename):
    """
    Fayl yuklovchining papkasiga tushadi:
        uploads/akmal-karimov-3f2a/IMG_0421.HEIC
    Kengaytma va nom o'zgarmaydi — sifat ham, metadata ham buzilmaydi.
    """
    folder = instance.folder_name or "nomalum"
    safe_name = os.path.basename(filename)[-120:]
    return f"uploads/{folder}/{uuid.uuid4().hex[:6]}__{safe_name}"


class Wedding(models.Model):
    """Taklifnomaning barcha matni va sozlamalari. Odatda bitta yozuv bo'ladi."""

    MODE_INVITATION = "invitation"
    MODE_THANKS = "thanks"
    MODE_CHOICES = [
        (MODE_INVITATION, "Taklifnoma (to'ygacha)"),
        (MODE_THANKS, "Rahmat sahifasi (to'ydan keyin)"),
    ]

    is_active = models.BooleanField("Faol", default=True)
    mode = models.CharField(
        "Sahifa rejimi", max_length=20, choices=MODE_CHOICES, default=MODE_INVITATION
    )

    groom_name = models.CharField("Kuyov ismi", max_length=80)
    bride_name = models.CharField("Kelin ismi", max_length=80)
    groom_name_en = models.CharField("Kuyov ismi (EN)", max_length=80, blank=True)
    bride_name_en = models.CharField("Kelin ismi (EN)", max_length=80, blank=True)

    event_at = models.DateTimeField("To'y sanasi va soati")
    welcome_time = models.CharField(
        "Kutib olish", max_length=40, blank=True, help_text="Masalan: 18:00"
    )

    venue_name = models.CharField("To'yxona nomi", max_length=160)
    venue_name_en = models.CharField("To'yxona nomi (EN)", max_length=160, blank=True)
    venue_address = models.CharField("Manzil", max_length=255, blank=True)
    venue_address_en = models.CharField("Manzil (EN)", max_length=255, blank=True)
    map_url = models.URLField("Xarita havolasi", blank=True, help_text="Yandex yoki Google Maps")
    latitude = models.FloatField("Kenglik", null=True, blank=True)
    longitude = models.FloatField("Uzunlik", null=True, blank=True)

    invite_text = models.TextField("Taklif matni", blank=True)
    invite_text_en = models.TextField("Taklif matni (EN)", blank=True)
    dress_code = models.CharField("Dress code", max_length=160, blank=True)
    dress_code_en = models.CharField("Dress code (EN)", max_length=160, blank=True)

    contact_one_name = models.CharField("1-aloqa: ism", max_length=80, blank=True)
    contact_one_phone = models.CharField("1-aloqa: telefon", max_length=40, blank=True)
    contact_two_name = models.CharField("2-aloqa: ism", max_length=80, blank=True)
    contact_two_phone = models.CharField("2-aloqa: telefon", max_length=40, blank=True)

    hero_image = models.ImageField("Bosh rasm", upload_to=hero_path, blank=True)
    music = models.FileField("Fon musiqasi", upload_to=music_path, blank=True)

    rsvp_open = models.BooleanField("Javob berish ochiq", default=True)
    uploads_open = models.BooleanField("Rasm yuklash ochiq", default=False)
    thanks_title = models.CharField("Rahmat sarlavhasi", max_length=160, blank=True)
    thanks_title_en = models.CharField("Rahmat sarlavhasi (EN)", max_length=160, blank=True)
    thanks_text = models.TextField("Rahmat matni", blank=True)
    thanks_text_en = models.TextField("Rahmat matni (EN)", blank=True)
    upload_hint = models.TextField("Yuklash bo'limi izohi", blank=True)
    upload_hint_en = models.TextField("Yuklash bo'limi izohi (EN)", blank=True)
    show_english = models.BooleanField(
        "Ingliz tili tugmasi", default=True,
        help_text="Belgini olsangiz sahifada til almashtirish tugmasi ko'rinmaydi."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "To'y"
        verbose_name_plural = "To'y sozlamalari"

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"

    @property
    def is_past(self):
        return timezone.now() > self.event_at


class TimelineEvent(models.Model):
    """Tanishuvdan to'ygacha bo'lgan voqealar."""

    wedding = models.ForeignKey(Wedding, related_name="timeline", on_delete=models.CASCADE)
    title = models.CharField("Sarlavha", max_length=120)
    title_en = models.CharField("Sarlavha (EN)", max_length=120, blank=True)
    date_label = models.CharField("Sana matni", max_length=60, blank=True)
    date_label_en = models.CharField("Sana matni (EN)", max_length=60, blank=True)
    text = models.TextField("Matn", blank=True)
    text_en = models.TextField("Matn (EN)", blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Voqea"
        verbose_name_plural = "Sevgi tarixi"

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    wedding = models.ForeignKey(Wedding, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField("Rasm", upload_to=gallery_path)
    caption = models.CharField("Izoh", max_length=160, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Galereya rasmi"
        verbose_name_plural = "Galereya"

    def __str__(self):
        return self.caption or f"Rasm #{self.pk}"


class Guest(models.Model):
    """
    Har bir mehmon uchun alohida havola: /?g=KOD
    Sahifa ochilganda "Hurmatli Akmal aka" deb murojaat qiladi.
    """

    wedding = models.ForeignKey(Wedding, related_name="guests", on_delete=models.CASCADE)
    name = models.CharField("Ism", max_length=120)
    honorific = models.CharField(
        "Murojaat", max_length=40, blank=True, help_text="aka, opa, xola, oila"
    )
    code = models.CharField("Kod", max_length=24, unique=True, blank=True)
    seats = models.PositiveSmallIntegerField("Necha kishiga", default=2)
    note = models.CharField("Ichki izoh", max_length=200, blank=True)
    opened_at = models.DateTimeField("Birinchi ochilgan", null=True, blank=True)
    open_count = models.PositiveIntegerField("Necha marta ochilgan", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Mehmon"
        verbose_name_plural = "Mehmonlar"

    def save(self, *args, **kwargs):
        if not self.code:
            base = slugify(self.name)[:12] or "mehmon"
            for _ in range(20):
                candidate = f"{base}-{_rand_code(4)}"
                if not Guest.objects.filter(code=candidate).exists():
                    self.code = candidate
                    break
            else:
                self.code = _rand_code(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return f"{self.name} {self.honorific}".strip()

    @property
    def invite_url(self):
        return f"{settings.SITE_URL}/?g={self.code}"


class Rsvp(models.Model):
    wedding = models.ForeignKey(Wedding, related_name="rsvps", on_delete=models.CASCADE)
    guest = models.ForeignKey(
        Guest, related_name="rsvps", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField("Ism", max_length=120)
    attending = models.BooleanField("Keladi", default=True)
    seats = models.PositiveSmallIntegerField("Necha kishi", default=1)
    phone = models.CharField("Telefon", max_length=40, blank=True)
    message = models.TextField("Tilak", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Javob"
        verbose_name_plural = "Mehmon javoblari (RSVP)"

    def __str__(self):
        holat = "keladi" if self.attending else "kelolmaydi"
        return f"{self.name} — {holat}"


class GuestUpload(models.Model):
    """
    To'ydan keyin mehmonlar yuklagan rasm va videolar.
    Fayl asl holida saqlanadi — siqilmaydi, o'lchami o'zgarmaydi.
    Faqat admin ko'radi va yuklab oladi.
    """

    wedding = models.ForeignKey(Wedding, related_name="uploads", on_delete=models.CASCADE)
    guest = models.ForeignKey(
        Guest, related_name="uploads", on_delete=models.SET_NULL, null=True, blank=True
    )
    uploader_name = models.CharField("Yuklovchi", max_length=120)
    folder_name = models.CharField("Papka", max_length=140, blank=True)
    file = models.FileField("Fayl", upload_to=guest_upload_path, storage=private_storage)
    original_name = models.CharField("Asl nomi", max_length=255, blank=True)
    content_type = models.CharField("Turi", max_length=100, blank=True)
    size = models.BigIntegerField("Hajmi (bayt)", default=0)
    caption = models.CharField("Izoh", max_length=200, blank=True)
    is_video = models.BooleanField("Video", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Yuklangan fayl"
        verbose_name_plural = "Mehmonlar yuklagan fayllar"
        indexes = [models.Index(fields=["folder_name"])]

    def save(self, *args, **kwargs):
        if not self.folder_name:
            base = slugify(self.uploader_name)[:24] or "mehmon"
            # Bir xil ism bir xil papkaga tushishi kerak — tasodifiy qism yo'q,
            # aks holda bitta odamning rasmlari bo'linib ketadi.
            suffix = self.guest.code if self.guest else "x"
            self.folder_name = f"{base}-{suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_name or os.path.basename(self.file.name)

    @property
    def size_mb(self):
        return round(self.size / (1024 * 1024), 2)
class Wish(models.Model):
    """
    Mehmonlar qoldirgan tilaklar. Sahifada hammaga ko'rinadi.
    Noo'rin yozuv chiqsa, admin «Ko'rinadi» belgisini olib tashlaydi.
    """

    wedding = models.ForeignKey(Wedding, related_name="wishes", on_delete=models.CASCADE)
    guest = models.ForeignKey(
        Guest, related_name="wishes", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField("Ism", max_length=120)
    text = models.TextField("Tilak")
    is_visible = models.BooleanField(
        "Ko'rinadi", default=True, help_text="Belgini olsangiz sahifadan yo'qoladi."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tilak"
        verbose_name_plural = "Tilaklar"

    def __str__(self):
        return f"{self.name}: {self.text[:40]}"


class Dua(models.Model):
    """
    Kelin-kuyovga baxt tilab o'qiladigan duolar.
    Matnlar admin panelidan tahrirlanadi, tartibi o'zgartiriladi.
    """

    wedding = models.ForeignKey(Wedding, related_name="duas", on_delete=models.CASCADE)
    title = models.CharField("Sarlavha", max_length=160)
    title_en = models.CharField("Sarlavha (EN)", max_length=160, blank=True)
    arabic = models.TextField("Arabcha matn", blank=True)
    transliteration = models.TextField("O'qilishi", blank=True)
    meaning = models.TextField("Ma'nosi")
    meaning_en = models.TextField("Ma'nosi (EN)", blank=True)
    source = models.CharField("Manba", max_length=160, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    is_visible = models.BooleanField("Ko'rinadi", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Duo"
        verbose_name_plural = "Duolar"

    def __str__(self):
        return self.title
