from django.urls import path

from . import views

app_name = 'foodie'
urlpatterns = [
    path(
        '',
        views.index,
        name='index'
    ),
    # ex: /foodie/login/
    path(
        'login/',
        views.foodie_login,
        name='login'
    ),
    # ex: /foodie/login/
    path(
        'login/auth/',
        views.foodie_login_auth,
        name='login_auth'
    ),
    # ex: /foodie/restaurants/4
    path(
        'restaurants/<int:restaurant_id>/',
        views.restaurant_profile,
        name='restaurant_profile'
    ),
    # ex: /foodie/recs #past lists should be hidden from user
    # and hard to find when monetizing?
    # would be free access to additonal recs
    path(
        'recs/',
        views.recs_list,
        name='recs'
    ),
    path(
        'recs/<str:saved>',
        views.recs_list,
        name='recs_saved'
    ),
    # ex: /foodie/users/
    # need to disguise user count in url
    path(
        'profile/',
        views.user_profile,
        name='user_profile'
    ),
    # ex: /foodie/users/2
    # need to disguise user count in url
    path(
        'users/<int:user_id>/',
        views.user_profile_by_id,
        name='user_profile_by_id'
    ),
    # handles recs savings
    path(
        'recs/save/<int:restaurant_id>/',
        views.save_restaurant,
        name='save_restaurant'
    ),
    # handles rec reviews
    path(
        'profile/review/<int:restaurant_id>/',
        views.review_restaurant,
        name='review_restaurant'
    ),
]
