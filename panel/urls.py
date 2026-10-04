from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.home, name="home"),
    path("kirish/", views.login_view, name="login"),
    path("chiqish/", views.logout_view, name="logout"),
    path("holat/", views.toggle, name="toggle"),

    path("toy/", views.wedding_edit, name="wedding"),
    path("yozuvlar/", views.labels, name="labels"),

    path("mehmonlar/", views.guests, name="guests"),
    path("mehmonlar/qoshish/", views.guest_add, name="guest-add"),
    path("mehmonlar/royxat/", views.guest_bulk, name="guest-bulk"),
    path("mehmonlar/csv/", views.guests_csv, name="guests-csv"),
    path("mehmonlar/qr.zip", views.guests_qr_zip, name="guests-qr-zip"),
    path("mehmonlar/<int:pk>/", views.guest_edit, name="guest-edit"),
    path("mehmonlar/<int:pk>/ochirish/", views.guest_delete, name="guest-delete"),
    path("mehmonlar/<int:pk>/qr.png", views.guest_qr, name="guest-qr"),

    path("javoblar/", views.rsvps, name="rsvps"),
    path("javoblar/csv/", views.rsvps_csv, name="rsvps-csv"),
    path("javoblar/<int:pk>/ochirish/", views.rsvp_delete, name="rsvp-delete"),

    path("tilaklar/", views.wishes, name="wishes"),
    path("tilaklar/hammasini-tasdiqlash/", views.wishes_approve_all, name="wishes-approve-all"),
    path("tilaklar/<int:pk>/", views.wish_action, name="wish-action"),

    path("galereya/", views.gallery, name="gallery"),
    path("galereya/<int:pk>/", views.gallery_item, name="gallery-item"),

    path("tarix/", views.timeline, name="timeline"),
    path("tarix/<int:pk>/", views.timeline_item, name="timeline-item"),

    path("duolar/", views.duas, name="duas"),
    path("duolar/<int:pk>/", views.dua_item, name="dua-item"),

    path("esdaliklar/", views.uploads, name="uploads"),
    path("esdaliklar/<str:folder>/", views.uploads_folder, name="uploads-folder"),
    path("esdaliklar/fayl/<int:pk>/ochirish/", views.upload_delete, name="upload-delete"),
]
