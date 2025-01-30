from django.urls import path

from . import views
app_name = "inference"

urlpatterns = [
    path("home/<str:definition>", views.home, name="home_main"),
    path("home/", views.home, name="home_empty"),
    path("guess/", views.guess, name="guess"),
]
