"""
Namuna ma'lumot to'ldiradi: ikkala tomon uchun ham to'y yaratadi,
shunda birinchi ishga tushirishdayoq ikkala sahifa to'liq ko'rinishda ochiladi.

    python manage.py seed_demo
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from invitation.models import Guest, Wedding


class Command(BaseCommand):
    help = "Namuna to'y ma'lumotlarini yaratadi (kuyov va kelin tomoni)"

    def handle(self, *args, **options):
        if Wedding.objects.exists():
            self.stdout.write(self.style.WARNING("To'y allaqachon yaratilgan. To'xtatildi."))
            return

        kun = timezone.now() + timedelta(days=45)

        umumiy = dict(
            groom_name="Javohir",
            bride_name="Nilufar",
            invite_text=(
                "Hayotimizning eng baxtli kunida yonimizda bo'lishingizni istaymiz. "
                "Sizni to'y marosimimizga chin dildan taklif qilamiz."
            ),
            dress_code="Klassik uslub",
            thanks_title="Kelganingiz uchun rahmat",
            thanks_text=(
                "O'sha kunni siz bilan birga o'tkazdik. Endi eng qimmatli qismi qoldi — "
                "o'sha kechada olgan rasm va videolaringizni shu yerga qoldiring."
            ),
            upload_hint=(
                "Telefoningiz galereyasidan tanlang. Fayllar asl sifatida saqlanadi, "
                "faqat kuyov-kelin ko'radi."
            ),
        )

        # Ikki tomon — ikki xil to'yxona, vaqt va aloqa raqami
        kuyov = Wedding.objects.create(
            slug="kuyov",
            title="Kuyov tomoni",
            is_default=True,
            event_at=kun.replace(hour=7, minute=0, second=0, microsecond=0),
            welcome_time="06:30",
            venue_name="Arana to'yxonasi",
            venue_address="Andijon viloyati, Marhamat tumani",
            latitude=40.520087,
            longitude=72.340367,
            contact_one_name="Sardor",
            contact_one_phone="+998 90 123 45 67",
            **umumiy,
        )
        kelin = Wedding.objects.create(
            slug="kelin",
            title="Kelin tomoni",
            event_at=kun.replace(hour=10, minute=0, second=0, microsecond=0),
            welcome_time="09:30",
            venue_name="Vohidjon ota to'yxonasi",
            venue_address="Toshkent shahri, Yunusobod tumani",
            latitude=41.3255,
            longitude=69.2874,
            contact_one_name="Dilnoza",
            contact_one_phone="+998 93 765 43 21",
            **umumiy,
        )

        namunalar = {
            kuyov: [("Akmal", "aka", 2), ("Bekzod", "", 2)],
            kelin: [("Zuhra", "opa", 4), ("Malika", "opa", 2)],
        }
        for wedding, royxat in namunalar.items():
            for name, honorific, seats in royxat:
                Guest.objects.create(
                    wedding=wedding, name=name, honorific=honorific, seats=seats
                )

        self.stdout.write(self.style.SUCCESS("Namuna ma'lumot yaratildi: 2 ta to'y."))
        for wedding in Wedding.objects.all():
            self.stdout.write(f"\n{wedding.title} — {wedding.page_url}")
            for guest in wedding.guests.all():
                self.stdout.write(f"  {guest.display_name:20} {guest.invite_url}")
