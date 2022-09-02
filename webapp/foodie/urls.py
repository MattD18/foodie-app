from django.urls import path

from . import views

app_name ='foodie'
urlpatterns = [
    path('', views.index, name='index'),
    # ex: /foodie/restaurants/4
    path('restaurants/<int:restaurant_id>/', views.restaurant_profile, name='restaurant_profile'),
    # ex: /foodie/recs #past lists should be hidden from user / hard to find when monetizing? would be free access to additonal recs
    path('recs/', views.recs_list, name='recs'),
    path('recs/<str:restaurant_saved>/', views.recs_list, name='recs_from_saved'),
    # ex: /foodie/users/2 
    path('users/<int:user_id>/', views.user_profile, name='user_profile'), ##need to disguise user count in url
    # handles recs savings
    path('recs/save/<int:restaurant_id>/', views.save_restaurant, name='save_restaurant'),
]