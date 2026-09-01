from django.urls import path

from . import views

urlpatterns = [
    # Ochiq API — taklifnoma sahifasi shulardan foydalanadi
    path("wedding/", views.wedding_detail, name="wedding-detail"),
    path("rsvp/", views.rsvp_create, name="rsvp-create"),
    path("uploads/", views.upload_create, name="upload-create"),
    path("wishes/", views.wish_create, name="wish-create"),
    # Faqat admin uchun — yuklangan fayllarni ko'rish va olish
    path("private/uploads/browser/", views.uploads_browser, name="uploads-browser"),
    path("private/uploads/all.zip", views.download_all, name="uploads-download-all"),
    path("private/uploads/folder/<str:folder>.zip", views.download_folder, name="uploads-download-folder"),
    path("private/uploads/<int:pk>/view/", views.upload_serve, name="upload-serve"),
    path("private/uploads/<int:pk>/download/", views.upload_download, name="upload-download"),
]
