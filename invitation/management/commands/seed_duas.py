"""
Kelin-kuyov uchun duolarni bazaga qo'shadi.

    python manage.py seed_duas

Faqat o'zbek manbalari bilan tasdiqlangan ikkita duo qo'shiladi:

  1-duo — arabcha matn Termiziy 1091, Abu Dovud 2123, Ibn Moja 1905
          rivoyatlaridan. O'zbekcha o'qilishi Chirchiq shahar «Markaziy»
          jome masjidining duolar to'plamida berilgan shaklda.

  2-duo — Furqon surasi 74-oyat. O'zbekcha o'qilishi aniq.uz saytidagi
          «Nikoh kechasida o'qiladigan duo» maqolasida berilgan shaklda.

Buyruq qayta ishga tushirilsa matnlar yangilanadi. Yangi duo qo'shmoqchi
bo'lsangiz admin paneldagi «Duolar» bo'limidan qo'shing — bu buyruq
sizning qo'shganingizga tegmaydi.
"""
from django.core.management.base import BaseCommand

from invitation.models import Dua, Wedding

DUAS = [
    {
        "order": 1,
        "title": "Yangi turmush qurganlarga aytiladigan duo",
        "arabic": "بَارَكَ اللّٰهُ لَكَ، وَبَارَكَ عَلَيْكَ، وَجَمَعَ بَيْنَكُمَا فِي خَيْرٍ",
        "transliteration": (
            "Baarokallohu laka va baaroka 'alayka "
            "va jama'a baynakumaa fiy xoyr."
        ),
        "meaning": (
            "Alloh senga baraka bersin, ustingga barakotlarini yog'dirsin "
            "va ikkovingizni yaxshilikda jamlasin."
        ),
        "meaning_en": (
            "May Allah bless you, and shower His blessings upon you, "
            "and join the two of you together in goodness."
        ),
        "source": "Termiziy 1091, Abu Dovud 2123, Ibn Moja 1905",
    },
    {
        "order": 2,
        "title": "Oila uchun duo",
        "arabic": (
            "رَبَّنَا هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ "
            "وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا"
        ),
        "transliteration": (
            "Robbana hablana min azvajina va zurriyyatina "
            "qurrota a'yunin vaj'alna lil-muttaqiyna imama."
        ),
        "meaning": (
            "Parvardigoro, jufti halollarimiz va zurriyotlarimizdan bizga "
            "ko'z quvonchini ato et, bizni taqvodorlarga peshvo qil."
        ),
        "meaning_en": (
            "Our Lord, grant us from among our spouses and offspring comfort to "
            "our eyes, and make us a model for the righteous."
        ),
        "source": "Furqon surasi, 74-oyat",
    },
]

# Oldingi versiyada qo'shilgan, endi ishlatilmaydigan duolar.
# Manbasi tasdiqlanmagani uchun olib tashlandi.
ESKI_SARLAVHALAR = [
    "Er-xotin o'rtasidagi mehr haqida",
    "Qisqa muborakbod duosi",
    "Yaxshilik so'rab qilinadigan duo",
]


class Command(BaseCommand):
    help = "Manbasi tasdiqlangan duolarni qo'shadi yoki yangilaydi"

    def handle(self, *args, **options):
        wedding = Wedding.objects.filter(is_active=True).first()
        if not wedding:
            self.stdout.write(self.style.ERROR("Avval to'y ma'lumotlarini kiriting."))
            return

        added = updated = 0
        for item in DUAS:
            data = dict(item)
            order = data.pop("order")
            _, created = Dua.objects.update_or_create(
                wedding=wedding, order=order, defaults=data
            )
            if created:
                added += 1
            else:
                updated += 1

        removed, _ = Dua.objects.filter(
            wedding=wedding, title__in=ESKI_SARLAVHALAR
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{added} ta qo'shildi, {updated} tasi yangilandi, "
                f"{removed} tasi o'chirildi."
            )
        )
        self.stdout.write("Admin paneldagi «Duolar» bo'limidan tahrirlashingiz mumkin.")