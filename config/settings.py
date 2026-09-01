"""
Django sozlamalari — to'y taklifnomasi loyihasi.
Barcha maxfiy qiymatlar .env faylidan o'qiladi.
"""
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini yuklaymiz (backend/.env)
load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    """Bo'sh qiymat (`KEY=`) kiritilmagan deb hisoblanadi va default ishlatiladi."""
    value = os.environ.get(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def env_bool(key, default=False):
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on", "ha")


def env_list(key, default=""):
    raw = os.environ.get(key, default) or ""
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------- asosiy
SECRET_KEY = env("DJANGO_SECRET_KEY", "almashtiring-bu-faqat-development-uchun")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
)

# Saytning ochiq manzili — QR kod va mehmon havolalari shu asosda quriladi
SITE_URL = env("SITE_URL", "http://127.0.0.1:8000").rstrip("/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "invitation",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------- baza
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "toy_taklifnoma"),
        "USER": env("POSTGRES_USER", "postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", "postgres"),
        "HOST": env("POSTGRES_HOST", "127.0.0.1"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------- til / vaqt
LANGUAGE_CODE = "uz"
TIME_ZONE = env("TIME_ZONE", "Asia/Tashkent")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------- fayllar
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Ochiq media: hero rasm, galereya, musiqa — hamma ko'radi
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Yopiq media: mehmonlar yuklagan rasm va videolar — faqat admin ko'radi.
# Bu papka hech qachon to'g'ridan-to'g'ri web orqali berilmaydi.
PRIVATE_MEDIA_ROOT = Path(env("PRIVATE_MEDIA_ROOT") or (BASE_DIR / "private_media"))

# Papkalar mavjudligiga ishonch hosil qilamiz
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
PRIVATE_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Katta video yuklash uchun. 2.5 MB dan katta fayl darhol diskka yoziladi
# (xotirada saqlanmaydi), shuning uchun 1 GB video ham RAM'ni to'ldirmaydi.
FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440
DATA_UPLOAD_MAX_MEMORY_SIZE = 2_621_440
MAX_UPLOAD_SIZE_MB = int(env("MAX_UPLOAD_SIZE_MB", "512"))
MAX_UPLOADS_PER_GUEST = int(env("MAX_UPLOADS_PER_GUEST", "60"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------- API
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("THROTTLE_ANON", "120/hour"),
        "upload": env("THROTTLE_UPLOAD", "200/hour"),
        "rsvp": env("THROTTLE_RSVP", "20/hour"),
    },
}

# Sayt va API bitta domenda ishlaydi, shuning uchun CORS odatda kerak emas.
# Kelajakda alohida frontend qo'shsangiz shu yerga manzilini yozasiz.
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOW_CREDENTIALS = False

# ---------------------------------------------------------------- xavfsizlik
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", "INFO")},
}
