
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("inference/", include("inference.urls")),
    path("admin/", admin.site.urls),
]
