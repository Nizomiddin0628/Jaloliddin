"""
Sahifada ko'rsatiladigan rasmlarni avtomatik siqadi.

Telefondan yuklangan rasm 3-5 MB bo'ladi va 4000 piksel kenglikda. Sahifada
u eng ko'pi bilan 1600 piksel ko'rinadi, demak qolgani behuda trafik.
200 ta mehmon sahifani ochsa, siqilmagan galereya gigabaytlab trafik yeydi
va mobil internetdagi mehmon uchun sayt qotib qolgandek tuyuladi.

MUHIM: bu faqat kuyov-kelin yuklaydigan rasmlarga tegishli — bosh rasm va
galereya. Mehmonlar yuklagan esdaliklarga HECH QACHON tegilmaydi, ular asl
sifatida saqlanadi.
"""
import io

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

MAX_SIDE = 1600
QUALITY = 82


def optimize(field, max_side=MAX_SIDE, quality=QUALITY):
    """
    Rasm maydonini joyida siqadi. Yangi yuklangan fayl bo'lmasa tegmaydi,
    shuning uchun har saqlashda qayta-qayta siqilmaydi.
    """
    if not field:
        return

    # Faqat hozir yuklangan faylni qayta ishlaymiz
    raw = getattr(field, "file", None)
    if not isinstance(raw, UploadedFile):
        return

    try:
        from PIL import Image, ImageOps
    except ImportError:
        return

    try:
        raw.seek(0)
        image = Image.open(raw)

        # Telefon rasmlari EXIF'da burilish burchagini saqlaydi —
        # uni hisobga olmasak rasm yonboshlab qoladi
        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            converted = image.convert("RGBA")
            background.paste(converted, mask=converted.split()[-1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        if max(image.size) > max_side:
            image.thumbnail((max_side, max_side), Image.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=True)

        name = field.name.rsplit("/", 1)[-1]
        stem = name.rsplit(".", 1)[0]
        field.save(f"{stem}.jpg", ContentFile(buffer.getvalue()), save=False)
    except Exception:
        # Siqib bo'lmasa asl faylni qoldiramiz — rasm yo'qolib qolmasin
        return