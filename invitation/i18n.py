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
        "today": "Bugun — to'y kuni!",
        "story_title": "Shu kungacha",
        "gallery_title": "Biz haqimizda",
        "gallery_title_thanks": "O'sha kundan",
        "event_title": "To'y marosimi",
        "fact_date": "Sana",
        "fact_time": "Vaqt",
        "fact_place": "Joy",
        "fact_dress": "Kiyim",
        "welcome_at": "Kutib olish",
        "starts_at": "Boshlanishi",
        "open_maps": "Google xaritada",
        "open_yandex": "Yandex xaritada",
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
        "wishes_lead": "Yosh oilaga bir og'iz yaxshi so'z qoldiring.",
        "your_wish": "Tilagingiz",
        "wish_placeholder": "Baxtli bo'linglar…",
        "send_wish": "Tilakni qoldirish",
        "no_wishes": "Hali tilak yo'q. Birinchi bo'lib siz yozing.",
        "wish_pending": "Tilagingiz yuborildi. Ko'rib chiqilgach sahifada paydo bo'ladi.",
        "wish_added": "Tilagingiz qo'shildi. Rahmat!",
        "prev_wish": "Oldingi tilak",
        "next_wish": "Keyingi tilak",
        "upload_title": "Esdalik rasmlarini yuklash",
        "upload_default_hint": "",
        "upload_note": "",
        "pick_gallery": "Galereyadan tanlash",
        "take_photo": "Hozir rasmga olish",
        "shoot": "Rasmga olish",
        "rec_start": "Video olish",
        "rec_stop": "To'xtatish",
        "close": "Yopish",
        "uploading": "Yuklanmoqda — sahifani yopmang.",
        "uploaded_count": "ta fayl yuklandi. Rahmat!",
        "upload_privacy": "",
        "footer_note": "Sizni ko'rishdan mamnun bo'lamiz.",
        "admin_panel": "Boshqaruv paneli",
        "scroll_hint": "Pastga suring",
        # --- yangi dizayn uchun
        "open_invite": "Taklifnomani ochish",
        "open_thanks": "Sahifani ochish",
        "you_are_invited": "Siz to'yimizga taklif qilingansiz",
        "nav_home": "Bosh",
        "nav_time": "Vaqt",
        "nav_place": "Manzil",
        "nav_rsvp": "Javob",
        "nav_wishes": "Tilaklar",
        "nav_photos": "Rasmlar",
        "nav_upload": "Yuklash",
        "add_calendar": "Kalendarga qo'shish",
        "directions": "Yo'nalishni ko'rish",
        "call": "Qo'ng'iroq qilish",
        "questions": "Savollar bo'lsa, qo'ng'iroq qiling",
        "people": "kishi",
        "change_answer": "Javobni o'zgartirish",
        "swipe_hint": "Rasmni suring",
        "music_on": "Musiqani yoqish",
        "music_off": "Musiqani o'chirish",
        "invite_title": "Sizni kutamiz",
        "and": "va",
        "err_name": "Ismingizni to'liqroq yozing.",
        "err_choice": "Kelasizmi yoki yo'q — belgilang.",
        "err_wish": "Tilagingizni yozing.",
        "err_send": "Yuborilmadi. Internetni tekshirib, qayta urinib ko'ring.",
        "err_name_first": "Avval ismingizni yozing — rasmlar shu nom bilan saqlanadi.",
        "st_waiting": "navbatda",
        "st_done": "yuklandi",
        "too_big": "MB dan katta",
        "drop_here": "Rasm va videolarni shu yerga tashlang",
        "cam_denied": "Kameraga ruxsat berilmadi. Brauzer so'roviga «Ruxsat berish» deng.",
        "cam_unsupported": "Bu brauzer kamerani qo'llab-quvvatlamaydi.",
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
        "open_maps": "Open in Google Maps",
        "open_yandex": "Open in Yandex Maps",
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
        "wishes_lead": "Leave a few kind words for the couple.",
        "your_wish": "Your wish",
        "wish_placeholder": "Wishing you a lifetime of happiness…",
        "send_wish": "Leave a wish",
        "no_wishes": "No wishes yet. Be the first to write one.",
        "wish_pending": "Your wish has been sent. It will appear once reviewed.",
        "wish_added": "Your wish has been added. Thank you!",
        "prev_wish": "Previous wish",
        "next_wish": "Next wish",
        "upload_title": "Share your photos",
        "upload_default_hint": "",
        "upload_note": "",
        "pick_gallery": "Choose from gallery",
        "take_photo": "Take a photo now",
        "shoot": "Capture",
        "rec_start": "Record video",
        "rec_stop": "Stop",
        "close": "Close",
        "uploading": "Uploading — please keep this page open.",
        "uploaded_count": "files uploaded. Thank you!",
        "upload_privacy": "",
        "footer_note": "We would be delighted to see you.",
        "admin_panel": "Admin panel",
        "scroll_hint": "Scroll down",
        "open_invite": "Open the invitation",
        "open_thanks": "Open the page",
        "you_are_invited": "You are invited to our wedding",
        "nav_home": "Home",
        "nav_time": "When",
        "nav_place": "Where",
        "nav_rsvp": "Reply",
        "nav_wishes": "Wishes",
        "nav_photos": "Photos",
        "nav_upload": "Upload",
        "add_calendar": "Add to calendar",
        "directions": "Get directions",
        "call": "Call",
        "questions": "Questions? Give us a call",
        "people": "people",
        "change_answer": "Change my answer",
        "swipe_hint": "Swipe the photos",
        "music_on": "Play music",
        "music_off": "Pause music",
        "invite_title": "Join us",
        "and": "and",
        "err_name": "Please write your full name.",
        "err_choice": "Please choose whether you can come.",
        "err_wish": "Please write your wish.",
        "err_send": "Not sent. Check your connection and try again.",
        "err_name_first": "Write your name first — your files are saved under it.",
        "st_waiting": "waiting",
        "st_done": "uploaded",
        "too_big": "MB limit exceeded",
        "drop_here": "Drop photos and videos here",
        "cam_denied": "Camera access was blocked. Allow it in the browser prompt.",
        "cam_unsupported": "This browser does not support the camera.",
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

# ----------------------------------------------------------------------------
# Admin panelidan o'zgartirsa bo'ladigan yozuvlar.
# Har bir guruh panelda alohida blok bo'lib chiqadi. Bo'sh qoldirilgan
# maydon o'rniga yuqoridagi standart matn ko'rsatiladi.
# ----------------------------------------------------------------------------

# Sahifa bo'limlari: har birining yoqib-o'chirgichi va o'zgartirsa bo'ladigan
# yozuvlari. Panel shu ro'yxat bo'yicha chiziladi, shuning uchun yangi bo'lim
# qo'shilganda faqat shu yerga bitta qator yoziladi.
#   (Wedding maydoni yoki None, bo'lim nomi, izoh, [(kalit, tushuntirish), ...])
SECTIONS = [
    (None, "Bosh ekran", "Mehmon ismi va kuyov-kelin ismlari — doim ko'rinadi", [
        ("dear", "Mehmon ismidan oldingi so'z"),
        ("greeting_note", "Ism ostidagi qator"),
        ("generic_label", "Umumiy havolada: ism o'rnidagi yozuv"),
        ("generic_name", "Umumiy havolada: murojaat"),
    ]),
    ("show_countdown", "Sanoq", "To'ygacha qolgan vaqt, to'q ko'k ekran", [
        ("countdown_title", "Sarlavha"),
        ("today", "To'y kuni sanoq o'rniga chiqadigan yozuv"),
        ("days", "«kun» yozuvi"),
        ("hours", "«soat» yozuvi"),
        ("minutes", "«daqiqa» yozuvi"),
        ("seconds", "«soniya» yozuvi"),
    ]),
    ("show_invite", "Taklif matni", "To'y ma'lumotlaridagi «Taklif matni» shu yerda chiqadi", []),
    ("show_gallery", "Galereya va slayd-shou", "Rasmlar bo'lmasa o'zi ko'rinmaydi", [
        ("gallery_title", "Sarlavha"),
        ("gallery_title_thanks", "Sarlavha (rahmat rejimida)"),
    ]),
    ("show_event", "Marosim va xarita", "Sana, vaqt, to'yxona va xarita", [
        ("event_title", "Sarlavha"),
        ("fact_date", "«Sana» yozuvi"),
        ("fact_time", "«Vaqt» yozuvi"),
        ("fact_place", "«Joy» yozuvi"),
        ("fact_dress", "«Kiyim» yozuvi"),
        ("welcome_at", "«Kutib olish» yozuvi"),
        ("starts_at", "«Boshlanishi» yozuvi"),
        ("open_maps", "Google xarita tugmasi"),
        ("open_yandex", "Yandex xarita tugmasi"),
    ]),
    ("show_duas", "Duolar", "Duolar bo'limidagi matnlar alohida sahifada", [
        ("duas_title", "Sarlavha"),
        ("duas_lead", "Sarlavha ostidagi izoh"),
    ]),
    ("show_wishes", "Tilaklar", "Mehmonlar tilak yozadi, siz tasdiqlaysiz", [
        ("wishes_title", "Sarlavha"),
        ("wishes_lead", "Sarlavha ostidagi izoh"),
        ("your_name", "«Ismingiz» yozuvi"),
        ("your_wish", "«Tilagingiz» yozuvi"),
        ("wish_placeholder", "Tilak maydonidagi namuna"),
        ("send_wish", "Yuborish tugmasi"),
        ("no_wishes", "Tilak yo'qligida chiqadigan yozuv"),
    ]),
    ("uploads_open", "Esdalik rasmlari", "To'ydan keyin mehmonlar rasm yuklaydi", [
        ("upload_title", "Sarlavha"),
        ("upload_note", "Yuklash maydonidagi izoh"),
        ("upload_privacy", "Pastdagi maxfiylik yozuvi"),
        ("pick_gallery", "«Galereyadan tanlash» tugmasi"),
        ("take_photo", "«Rasmga olish» tugmasi"),
    ]),
    ("show_music", "Fon musiqasi", "O'ngdagi pastki burchakdagi tugma", []),
    (None, "Sahifa oxiri", "Eng pastdagi yozuv va telefon raqamlar", [
        ("footer_note", "Oxiridagi yozuv"),
    ]),
]

# Bo'limni yoqib-o'chiradigan maydonlar — panel faqat shularni saqlashi mumkin
SECTION_FIELDS = [field for field, _, _, _ in SECTIONS if field]

EDITABLE_KEYS = {key for _, _, _, items in SECTIONS for key, _ in items}


def ui(lang, wedding=None):
    """Standart yozuvlar + admin o'zgartirganlari."""
    texts = dict(UI[lang])
    custom = {}
    if wedding is not None and isinstance(getattr(wedding, "labels", None), dict):
        custom = wedding.labels.get(lang) or {}
    for key, value in custom.items():
        if key in EDITABLE_KEYS and isinstance(value, str) and value.strip():
            texts[key] = value.strip()
    return texts
