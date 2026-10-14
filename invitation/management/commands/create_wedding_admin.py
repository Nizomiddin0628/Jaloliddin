"""
Do'stingiz uchun admin hisobi ochadi. U to'y ma'lumotini tahrirlaydi,
mehmonlarni qo'shadi, javoblarni va yuklangan rasmlarni ko'radi —
lekin boshqa foydalanuvchilarni boshqara olmaydi (super admin — siz).

    python manage.py create_wedding_admin javohir --password "kuchli-parol" --toy kelin

--toy berilsa, hisob o'sha to'yga biriktiriladi va panelda faqat shu
to'yning mehmonlari, tilaklari va rasmlari ko'rinadi.
"""
from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError

from invitation.models import Wedding

GROUP_NAME = "Toy adminlari"

MODEL_PERMS = {
    "wedding": ["view", "change"],
    "galleryphoto": ["view", "add", "change", "delete"],
    "guest": ["view", "add", "change", "delete"],
    "guestupload": ["view", "delete"],
    "wish": ["view", "change", "delete"],
    "dua": ["view", "add", "change", "delete"],
}


class Command(BaseCommand):
    help = "To'y egasi uchun cheklangan admin hisobi yaratadi"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="")
        parser.add_argument(
            "--toy", default="", help="To'yning havoladagi nomi: kuyov yoki kelin",
        )

    def handle(self, *args, **options):
        username = options["username"]
        wedding = None
        if options["toy"]:
            wedding = Wedding.objects.filter(slug=options["toy"]).first()
            if wedding is None:
                nomlar = ", ".join(Wedding.objects.values_list("slug", flat=True)) or "yo'q"
                raise CommandError(f"'{options['toy']}' nomli to'y topilmadi. Bor to'ylar: {nomlar}")

        existing = User.objects.filter(username=username).first()
        if existing and existing.is_superuser:
            raise CommandError(f"'{username}' allaqachon super admin.")

        group, _ = Group.objects.get_or_create(name=GROUP_NAME)
        perms = []
        for model, actions in MODEL_PERMS.items():
            for action in actions:
                perm = Permission.objects.filter(
                    codename=f"{action}_{model}",
                    content_type__app_label="invitation",
                ).first()
                if perm:
                    perms.append(perm)
        group.permissions.set(perms)

        # Buyruqni qayta ishga tushirsangiz — yangi ruxsatlar va parol beriladi
        if existing:
            user = existing
            user.set_password(options["password"])
            user.is_staff = True
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                password=options["password"],
                email=options["email"],
                is_staff=True,
                is_superuser=False,
            )
        user.groups.add(group)
        if wedding:
            wedding.editors.add(user)

        self.stdout.write(self.style.SUCCESS(f"'{username}' admin sifatida yaratildi."))
        if wedding:
            self.stdout.write(f"Biriktirilgan to'y: {wedding} ({wedding.slug})")
        else:
            self.stdout.write(self.style.WARNING(
                "To'y biriktirilmadi — hisob hech qaysi to'yni ko'rmaydi. "
                "--toy kuyov yoki --toy kelin bilan qayta yurgizing."
            ))
        self.stdout.write(f"Ruxsatlar: {len(perms)} ta. Guruh: {GROUP_NAME}")
        self.stdout.write("Kirish manzili: /panel/")
