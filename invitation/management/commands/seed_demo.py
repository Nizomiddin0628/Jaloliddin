"""
Namuna ma'lumot to'ldiradi, shunda birinchi ishga tushirishdayoq
sahifa bo'sh emas, to'liq ko'rinishda ochiladi.

    python manage.py seed_demo
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from invitation.models import Guest, TimelineEvent, Wedding


class Command(BaseCommand):
    help = "Namuna to'y ma'lumotlarini yaratadi"

    def handle(self, *args, **options):
        if Wedding.objects.exists():
            self.stdout.write(self.style.WARNING("To'y allaqachon yaratilgan. To'xtatildi."))
            return

        wedding = Wedding.objects.create(
            groom_name="Javohir",
            bride_name="Nilufar",
            event_at=timezone.now() + timedelta(days=45),
            welcome_time="18:00",
            venue_name="Zarafshon to'yxonasi",
            venue_address="Toshkent shahri, Yunusobod tumani, Amir Temur ko'chasi 108",
            map_url="https://yandex.uz/maps/",
            latitude=41.3255,
            longitude=69.2874,
            invite_text=(
                "Hayotimizning eng baxtli kunida yonimizda bo'lishingizni istaymiz. "
                "Sizni to'y marosimimizga chin dildan taklif qilamiz."
            ),
            dress_code="Klassik uslub",
            contact_one_name="Sardor",
            contact_one_phone="+998 90 123 45 67",
            contact_two_name="Dilnoza",
            contact_two_phone="+998 93 765 43 21",
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

        voqealar = [
            ("Birinchi uchrashuv", "2023-yil, kuz", "Do'stlar davrasida tanishdik."),
            ("Fotiha to'yi", "2026-yil, mart", "Ikki oila bir dasturxon atrofida yig'ildi."),
            ("To'y kuni", "Yaqinda", "Sizni ham shu quvonchga sherik bo'lishga chorlaymiz."),
        ]
        for i, (title, date_label, text) in enumerate(voqealar):
            TimelineEvent.objects.create(
                wedding=wedding, title=title, date_label=date_label, text=text, order=i
            )

        namunalar = [("Akmal", "aka", 2), ("Zuhra", "opa", 4), ("Bekzod", "", 2)]
        for name, honorific, seats in namunalar:
            Guest.objects.create(
                wedding=wedding, name=name, honorific=honorific, seats=seats
            )

        self.stdout.write(self.style.SUCCESS("Namuna ma'lumot yaratildi."))
        self.stdout.write("\nMehmon havolalari:")
        for guest in Guest.objects.all():
            self.stdout.write(f"  {guest.display_name:20} {guest.invite_url}")
