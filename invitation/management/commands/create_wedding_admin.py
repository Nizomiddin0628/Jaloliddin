"""
Do'stingiz uchun admin hisobi ochadi. U to'y ma'lumotini tahrirlaydi,
mehmonlarni qo'shadi, javoblarni va yuklangan rasmlarni ko'radi —
lekin boshqa foydalanuvchilarni boshqara olmaydi (super admin — siz).

    python manage.py create_wedding_admin javohir --password "kuchli-parol"
"""
from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError

GROUP_NAME = "Toy adminlari"

MODEL_PERMS = {
    "wedding": ["view", "change"],
    "timelineevent": ["view", "add", "change", "delete"],
    "galleryphoto": ["view", "add", "change", "delete"],
    "guest": ["view", "add", "change", "delete"],
    "rsvp": ["view", "delete"],
    "guestupload": ["view", "delete"],
}


class Command(BaseCommand):
    help = "To'y egasi uchun cheklangan admin hisobi yaratadi"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="")

    def handle(self, *args, **options):
        username = options["username"]
        if User.objects.filter(username=username).exists():
            raise CommandError(f"'{username}' allaqachon mavjud.")

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

        user = User.objects.create_user(
            username=username,
            password=options["password"],
            email=options["email"],
            is_staff=True,
            is_superuser=False,
        )
        user.groups.add(group)

        self.stdout.write(self.style.SUCCESS(f"'{username}' admin sifatida yaratildi."))
        self.stdout.write(f"Ruxsatlar: {len(perms)} ta. Guruh: {GROUP_NAME}")
        self.stdout.write("Kirish manzili: /admin/")
