"""
Disk va esdaliklar hajmini ko'rsatadi.

    python manage.py disk_report

To'y kunlari kuniga bir marta ishlatib turing — disk to'lib qolsa
mehmonlar rasm yuklay olmaydi.
"""
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum

from invitation.models import GuestUpload


def human(num_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


class Command(BaseCommand):
    help = "Disk bandligi va yuklangan esdaliklar hajmi"

    def handle(self, *args, **options):
        total, used, free = shutil.disk_usage(settings.BASE_DIR)
        percent = used / total * 100

        uploads = GuestUpload.objects.aggregate(n=Sum("size"))["n"] or 0
        count = GuestUpload.objects.count()

        self.stdout.write("")
        self.stdout.write(f"  Disk:        {human(used)} / {human(total)} ({percent:.0f}%)")
        self.stdout.write(f"  Bo'sh joy:   {human(free)}")
        self.stdout.write(f"  Esdaliklar:  {count} ta fayl, {human(uploads)}")
        self.stdout.write("")

        if percent > 85:
            self.stdout.write(self.style.ERROR(
                "  DIQQAT: disk to'lmoqda. Rasmlarni yuklab olib, "
                "eskilarini o'chiring yoki tarifni oshiring."
            ))
        elif percent > 70:
            self.stdout.write(self.style.WARNING(
                "  Disk yarmidan ko'pi band. Kuzatib turing."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  Joy yetarli."))
        self.stdout.write("")