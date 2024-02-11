from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.index, name='twilio'),
    path("message/", views.reply),
    path("login/", views.sms_login, name='login'),
    path("upload_warehouse/", views.upload_warehouse, name='upload_warehouse'),
    path("download_features/", views.download_features, name='download_features'),
    path("download_restaurants/", views.download_restaurants, name='download_restaurants'),
    
]