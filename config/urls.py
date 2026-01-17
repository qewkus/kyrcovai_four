from config import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("mailing.urls", namespace="mailing")),
    path("", include("users.urls", namespace="users")),
]

if settings.DEBUG:
    pass
