from django.contrib import admin
from django.urls import path

from config.views import health_check
from support.views import chat


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("api/chat/", chat, name="chat"),
]

