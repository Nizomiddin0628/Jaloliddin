"""
Sahifadagi tayyor matnlar ikki tilda.
Bazadagi matnlar (taklif matni, to'yxona nomi) admin panelidan kiritiladi —
bu yerda faqat tugma va sarlavha yozuvlari turadi.
"""

LANGS = ("uz", "en")

MONTHS = {
    "uz": [
        "yanvar", "fevral", "mart", "aprel", "may", "iyun",
        "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
    ],
    "en": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ],
}

WEEKDAYS = {
    "uz": [
        "yakshanba", "dushanba", "seshanba", "chorshanba",
        "payshanba", "juma", "shanba",
    ],
    "en": [
        "Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday",
    ],
}

UI = {
    "uz": {
        "dear": "Hurmatli",
        "greeting_note": "sizni to'y marosimimizga taklif qilamiz",
        "generic_label": "Taklifnoma",
        "generic_name": "Sizni to'yimizga chorlaymiz",
        "countdown_title": "To'ygacha qolgan vaqt",
        "days": "kun",
        "hours": "soat",
        "minutes": "daqiqa",
        "seconds": "soniya",
        "today": "Bugun — o'sha kun.",
        "story_title": "Shu kungacha",
        "gallery_title": "Biz haqimizda",
        "gallery_title_thanks": "O'sha kundan",
        "event_title": "Marosim",
        "fact_date": "Sana",
        "fact_time": "Vaqt",
        "fact_place": "Joy",
        "fact_dress": "Kiyim",
        "welcome_at": "Kutib olish",
        "starts_at": "Boshlanishi",
        "open_maps": "Navigatorda ochish",
        "rsvp_title": "Kelasizmi?",
        "rsvp_title_named": "{name}, kelasizmi?",
        "rsvp_lead": "Javobingiz oshpazga aniq son aytishimizga yordam beradi.",
        "your_name": "Ismingiz",
        "your_answer": "Javobingiz",
        "coming": "Kelaman",
        "not_coming": "Kelolmayman",
        "how_many": "Necha kishi bo'lasiz",
        "your_phone": "Telefon raqamingiz",
        "send_answer": "Javobni yuborish",
        "sending": "Yuborilmoqda",
        "rsvp_done_yes": "Javobingiz qabul qilindi",
        "rsvp_done_no": "Xabaringiz yetdi",
        "rsvp_done_yes_text": "Sizni kutamiz. Kelolmay qolsangiz, shu sahifadan qayta xabar bering.",
        "rsvp_done_no_text": "Afsus, lekin xabar berganingiz uchun rahmat.",
        "duas_title": "Duolar",
        "duas_lead": "Kelin-kuyovga baxt tilab ushbu duolarni o'qing.",
        "dua_prev": "Oldingi duo",
        "dua_next": "Keyingi duo",
        "wishes_title": "Tilaklar",
        "wishes_lead": "Yosh oilaga bir og'iz yaxshi so'z qoldiring — hammaga ko'rinadi.",
        "your_wish": "Tilagingiz",
        "wish_placeholder": "Baxtli bo'linglar…",
        "send_wish": "Tilakni qoldirish",
        "no_wishes": "Hali tilak yo'q. Birinchi bo'lib siz yozing.",
        "prev_wish": "Oldingi tilak",
        "next_wish": "Keyingi tilak",
        "upload_title": "Esdalik rasmlarini yuklash",
        "upload_default_hint": "O'sha kunda olgan rasm va videolaringizni shu yerga qoldiring.",
        "upload_note": "Rasm va videolar asl sifatida saqlanadi — siqilmaydi.",
        "pick_gallery": "Galereyadan tanlash",
        "take_photo": "Hozir rasmga olish",
        "shoot": "Rasmga olish",
        "close": "Yopish",
        "uploading": "Yuklanmoqda — sahifani yopmang.",
        "uploaded_count": "ta fayl yuklandi. Rahmat!",
        "upload_privacy": "Yuklangan fayllarni faqat kuyov va kelin ko'radi, sahifada hech kimga ko'rinmaydi.",
        "footer_note": "Sizni ko'rishdan mamnun bo'lamiz.",
        "admin_panel": "Boshqaruv paneli",
        "scroll_hint": "Pastga suring",
    },
    "en": {
        "dear": "Dear",
        "greeting_note": "we warmly invite you to our wedding",
        "generic_label": "Invitation",
        "generic_name": "You are invited to our wedding",
        "countdown_title": "Time left until the wedding",
        "days": "days",
        "hours": "hours",
        "minutes": "minutes",
        "seconds": "seconds",
        "today": "Today is the day.",
        "story_title": "Our story",
        "gallery_title": "About us",
        "gallery_title_thanks": "From that day",
        "event_title": "The celebration",
        "fact_date": "Date",
        "fact_time": "Time",
        "fact_place": "Venue",
        "fact_dress": "Dress code",
        "welcome_at": "Welcome from",
        "starts_at": "Starts at",
        "open_maps": "Open in maps",
        "rsvp_title": "Will you join us?",
        "rsvp_title_named": "{name}, will you join us?",
        "rsvp_lead": "Your answer helps us plan the seating and the meal.",
        "your_name": "Your name",
        "your_answer": "Your answer",
        "coming": "I will come",
        "not_coming": "I cannot come",
        "how_many": "How many of you",
        "your_phone": "Your phone number",
        "send_answer": "Send answer",
        "sending": "Sending",
        "rsvp_done_yes": "Your answer has been received",
        "rsvp_done_no": "Thank you for letting us know",
        "rsvp_done_yes_text": "We look forward to seeing you. If plans change, just answer again here.",
        "rsvp_done_no_text": "We will miss you, but thank you for telling us.",
        "duas_title": "Prayers",
        "duas_lead": "Read these prayers, wishing happiness for the bride and groom.",
        "dua_prev": "Previous prayer",
        "dua_next": "Next prayer",
        "wishes_title": "Wishes",
        "wishes_lead": "Leave a few kind words for the couple — everyone can read them.",
        "your_wish": "Your wish",
        "wish_placeholder": "Wishing you a lifetime of happiness…",
        "send_wish": "Leave a wish",
        "no_wishes": "No wishes yet. Be the first to write one.",
        "prev_wish": "Previous wish",
        "next_wish": "Next wish",
        "upload_title": "Share your photos",
        "upload_default_hint": "Leave the photos and videos you took that day right here.",
        "upload_note": "Photos and videos are kept at original quality — nothing is compressed.",
        "pick_gallery": "Choose from gallery",
        "take_photo": "Take a photo now",
        "shoot": "Capture",
        "close": "Close",
        "uploading": "Uploading — please keep this page open.",
        "uploaded_count": "files uploaded. Thank you!",
        "upload_privacy": "Only the bride and groom can see these files. They never appear on this page.",
        "footer_note": "We would be delighted to see you.",
        "admin_panel": "Admin panel",
        "scroll_hint": "Scroll down",
    },
}


def clean_lang(value):
    """Havoladagi ?lang= qiymatini tekshiradi."""
    value = (value or "").strip().lower()
    return value if value in LANGS else "uz"


def pick(obj, field, lang):
    """
    Inglizcha maydon to'ldirilgan bo'lsa o'shani, aks holda o'zbekchasini beradi.
    Shunday qilib do'stingiz hamma matnni tarjima qilishga majbur emas.
    """
    if lang == "en":
        value = getattr(obj, f"{field}_en", "") or ""
        if value.strip():
            return value
    return getattr(obj, field, "") or ""


def format_date(dt, lang):
    if lang == "en":
        return f"{MONTHS['en'][dt.month - 1]} {dt.day}, {dt.year}"
    return f"{dt.day}-{MONTHS['uz'][dt.month - 1]}, {dt.year}"


def weekday(dt, lang):
    return WEEKDAYS[lang][int(dt.strftime("%w"))]