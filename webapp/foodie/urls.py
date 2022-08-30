from django.urls import path

from . import views

app_name ='foodie'
urlpatterns = [
    path('', views.index, name='index'),
    # ex: /foodie/restaurants/4
    path('restaurants/<int:restaurant_id>/', views.restaurant_profile, name='profile'),
    # ex: /foodie/recs #past lists should be hidden from user / hard to find when monetizing? would be free access to additonal recs
    #path('recs/<int:list_id>', views.list, name='recs'),
]