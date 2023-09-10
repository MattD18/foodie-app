from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.index, name='twilio'),
    path("message/", views.reply),
]