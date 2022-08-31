from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Restaurant, RestaurantList, User

def index(request):
    return HttpResponse("Hello, world. You're at the foodie index.")

def restaurant_profile(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return render(request, 'foodie/restaurant_profile.html', {'restaurant':restaurant})


def _get_restaurant_object_list(list:RestaurantList):
    restaurant_id_list = list.restaurant_list
    restaurant_object_list = []
    for rid in restaurant_id_list:
        restaurant = get_object_or_404(Restaurant, pk=rid)
        restaurant_object_list.append(restaurant)
    return restaurant_object_list

def recs_list(request):
    # TODO: personalize recs to user
    recs_list = get_object_or_404(RestaurantList, pk=1) #HARDECODED for now
    restaurant_object_list = _get_restaurant_object_list(recs_list)
    context = {
        'recs_list':recs_list,
        'restaurant_list':restaurant_object_list
    }
    return render(request, 'foodie/recommendations.html', context)

def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_restaurant_list_id = user.user_restaurant_list
    user_restaurant_list = get_object_or_404(RestaurantList, pk=user_restaurant_list_id)
    user_restaurant_object_list = _get_restaurant_object_list(user_restaurant_list)
    context = {
        'user':user,
        'user_restaurant_list':user_restaurant_object_list
    }
    return render(request, 'foodie/user_profile.html', context)


