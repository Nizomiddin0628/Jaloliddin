from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from invitation import views as invitation_views

admin.site.site_header = "To'y taklifnomasi — boshqaruv"
admin.site.site_title = "Taklifnoma admin"
admin.site.index_title = "Boshqaruv paneli"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("invitation.urls")),
    path("panel/", include("panel.urls")),
    # Ildiz — mehmon kodiga yoki asosiy to'yga yo'naltiradi (eski havolalar uchun)
    path("", invitation_views.root_redirect, name="invitation-root"),
    # Har bir to'y o'z havolasida: /kuyov/, /kelin/
    path("<slug:slug>/", invitation_views.invitation_page, name="invitation-page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
