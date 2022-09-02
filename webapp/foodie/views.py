from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Restaurant, RestaurantList, FoodieUser, Engagement

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

def recs_list(request, restaurant_saved=''):

    user = authenticate(request, phone_number='347-555-0002')
    if user is not None:
        login(request, user)
    else:
        return HttpResponseNotFound('User not logged in')


    recs_list = get_object_or_404(RestaurantList, pk=1) #HARDECODED for now
    restaurant_object_list = _get_restaurant_object_list(recs_list)
    context = {
        'recs_list':recs_list,
        'restaurant_list':restaurant_object_list
    }
    if restaurant_saved=='':
        # log impression
        # user_id=2
        # user = get_object_or_404(FoodieUser, pk=user_id)
        for restaurant_id in recs_list.restaurant_list:
            restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
            _log_engagement(user, restaurant, 'impression')


    return render(request, 'foodie/recommendations.html', context)

def user_profile_by_id(request, user_id):
    user = get_object_or_404(FoodieUser, pk=user_id)
    user_restaurant_list_id = user.saved_list
    user_restaurant_list = get_object_or_404(RestaurantList, pk=user_restaurant_list_id)
    user_restaurant_object_list = _get_restaurant_object_list(user_restaurant_list)
    context = {
        'user':user,
        'user_restaurant_list':user_restaurant_object_list
    }
    return render(request, 'foodie/user_profile.html', context)

def user_profile(request):

    user=request.user
    print(user)
    if user is not None:
        login(request, user)
        user_id = request.user.id
        user = get_object_or_404(FoodieUser, pk=user_id)
        user_restaurant_list_id = user.saved_list
        user_restaurant_list = get_object_or_404(RestaurantList, pk=user_restaurant_list_id)
        user_restaurant_object_list = _get_restaurant_object_list(user_restaurant_list)
        context = {
            'user':user,
            'user_restaurant_list':user_restaurant_object_list
        }
        return render(request, 'foodie/user_profile.html', context)
    else:
        return HttpResponseNotFound('User not logged in')


def _log_engagement(user, restaurant, engagement_type):
    #log result in engagement as well
    e = Engagement(
        user=user,
        restaurant=restaurant,
        action=engagement_type
    )
    e.save()
    return

def save_restaurant(request, restaurant_id):
    '''
    append restaurant id to users save list
    need to make response redirect dynamic on page where list was

    #TODO: dynamically choose user, for now just hard code
    '''
    # user_id =2
    # user = get_object_or_404(FoodieUser, pk=user_id)
    user=request.user
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    user_restaurant_list_object = get_object_or_404(RestaurantList, pk=user.saved_list)
    user_restaurant_list = user_restaurant_list_object.restaurant_list
    if not restaurant_id in user_restaurant_list:
        user_restaurant_list.append(restaurant_id)
        user_restaurant_list_object.restaurant_list = user_restaurant_list
        user_restaurant_list_object.save()

        _log_engagement(user, restaurant, 'save')
    else: 
        pass
    
    return HttpResponseRedirect('/foodie/recs/restaurant_saved')