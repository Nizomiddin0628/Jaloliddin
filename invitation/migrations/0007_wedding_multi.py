"""
Bir saytda bir nechta to'y: kuyov tomoni va kelin tomoni.

Mavjud to'y yozuvi «kuyov» havolasini oladi va asosiy to'y bo'lib qoladi,
shuning uchun eski havolalar ishlashda davom etadi. Hech qanday ma'lumot
o'chirilmaydi — faqat yangi maydonlar qo'shiladi.
"""
from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    """Har bir mavjud to'yga takrorlanmas havola nomi beramiz."""
    Wedding = apps.get_model("invitation", "Wedding")
    taken = set()
    for i, w in enumerate(Wedding.objects.order_by("id")):
        base = slugify(w.groom_name)[:24] or "toy"
        name = "kuyov" if i == 0 else base
        n = 2
        while name in taken:
            name = f"{base}-{n}"
            n += 1
        taken.add(name)
        w.slug = name
        w.is_default = i == 0
        Wedding.objects.filter(pk=w.pk).update(slug=name, is_default=w.is_default)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("invitation", "0006_wedding_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="wedding",
            name="slug",
            # db_index=False — maydon shu yerda indekssiz qo'shiladi. Aks holda
            # pastdagi AlterField unique qilganda PostgreSQL o'sha nomli
            # «...slug_..._like» indeksini ikkinchi marta yaratmoqchi bo'ladi
            # va migratsiya «already exists» xatosi bilan to'xtaydi.
            field=models.SlugField(
                default="", max_length=30, db_index=False, verbose_name="Havoladagi nom",
                help_text="Sayt manzilida shu ko'rinadi: sayt.uz/kuyov/ — faqat lotin harflari.",
            ),
        ),
        migrations.AddField(
            model_name="wedding",
            name="title",
            field=models.CharField(
                blank=True, max_length=60, verbose_name="To'y nomi",
                help_text="Panelda ajratib turish uchun. Masalan: «Kuyov tomoni».",
            ),
        ),
        migrations.AddField(
            model_name="wedding",
            name="is_default",
            field=models.BooleanField(
                default=False, verbose_name="Asosiy to'y",
                help_text="Domen kodsiz ochilganda shu to'y ko'rsatiladi.",
            ),
        ),
        migrations.AddField(
            model_name="wedding",
            name="editors",
            field=models.ManyToManyField(
                blank=True, related_name="weddings", to=settings.AUTH_USER_MODEL,
                verbose_name="Adminlar",
                help_text="Shu to'yni boshqaradigan hisoblar. Super admin hammasini ko'radi.",
            ),
        ),
        # Avval qiymat beramiz, keyin takrorlanmas qilamiz — shunda eski
        # yozuvlar bo'sh slug bilan to'qnashmaydi.
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="wedding",
            name="slug",
            field=models.SlugField(
                max_length=30, unique=True, verbose_name="Havoladagi nom",
                help_text="Sayt manzilida shu ko'rinadi: sayt.uz/kuyov/ — faqat lotin harflari.",
            ),
        ),
        migrations.AlterModelOptions(
            name="wedding",
            options={
                "ordering": ["-is_default", "id"],
                "verbose_name": "To'y",
                "verbose_name_plural": "To'y sozlamalari",
            },
        ),
    ]
