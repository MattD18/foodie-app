from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import (
    Restaurant,
    RestaurantList,
    FoodieUser,
    Engagement, 
    UserRecList,
    UserRestaurantReview,
)


def _log_engagement(user, restaurant, engagement_type):
    '''
    log result in engagement as well
    '''
    e = Engagement(
        user=user,
        restaurant=restaurant,
        action=engagement_type
    )
    e.save()
    return


def _create_new_user(phone_number):
    # create user w/ save list
    rl = RestaurantList(
        restaurant_list=[]
    )
    rl.save()
    u = FoodieUser(
        phone_number=phone_number,
        saved_list=rl.id
    )
    u.save()
    # initiate user's rec list / statically set
    # update with zip code later
    rl = RestaurantList.objects.get(pk=1)
    url = UserRecList(user=u, restaurant_list=rl)
    url.save()
    return u


def index(request):
    return HttpResponse("Hello, world. You're at the foodie index.")


def restaurant_profile(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return render(
        request, 'foodie/restaurant_profile.html', {'restaurant': restaurant}
    )


def _get_restaurant_object_list(list: RestaurantList):
    restaurant_id_list = list.restaurant_list
    restaurant_object_list = []
    for rid in restaurant_id_list:
        restaurant = get_object_or_404(Restaurant, pk=rid)
        restaurant_object_list.append(restaurant)
    return restaurant_object_list


@login_required
def recs_list(request, saved=None):
    user = request.user
    user_rec_list = UserRecList.objects.filter(user=user)[0]
    recs_list = get_object_or_404(
        RestaurantList,
        pk=user_rec_list.restaurant_list_id
    )
    restaurant_object_list = _get_restaurant_object_list(recs_list)
    context = {
        'recs_list': recs_list,
        'restaurant_list': restaurant_object_list,
    }
    if not saved:
        # log impression
        for restaurant_id in recs_list.restaurant_list:
            restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
            _log_engagement(user, restaurant, 'impression')
    return render(request, 'foodie/recommendations.html', context)


def foodie_login(request):
    return render(request, 'foodie/login.html')


def foodie_login_auth(request):
    phone_number = request.POST['phone_number']
    user = authenticate(request, phone_number=phone_number)
    if user is not None:
        login(request, user)
        return redirect('/foodie/recs')
    else:
        new_user = _create_new_user(phone_number=phone_number)
        login(request, new_user)
        return redirect('/foodie/onboarding')


def onboarding(request):
    return render(request, 'foodie/onboarding.html')


@login_required
def onboarding_first_rec(request):
    user = request.user
    # update user with neighborhood info,
    # can later expand to add other info
    user.neighborhood = request.POST['neighborhood']
    user.save()
    # TODO: add new custom rec list based on onboarding info
    return redirect('/foodie/recs')


def user_profile_by_id(request, user_id):
    user = get_object_or_404(FoodieUser, pk=user_id)
    user_restaurant_list_id = user.saved_list
    user_restaurant_list = get_object_or_404(
        RestaurantList, pk=user_restaurant_list_id
    )
    user_restaurant_object_list = _get_restaurant_object_list(
        user_restaurant_list
    )
    context = {
        'user': user,
        'user_restaurant_list': user_restaurant_object_list
    }
    return render(request, 'foodie/user_profile.html', context)


@login_required
def user_profile(request):
    user = request.user
    user_restaurant_list_id = user.saved_list
    user_restaurant_list = get_object_or_404(
        RestaurantList, pk=user_restaurant_list_id
    )
    user_restaurant_object_list = _get_restaurant_object_list(
        user_restaurant_list
    )
    context = {
        'user': user,
        'user_restaurant_list': user_restaurant_object_list
    }
    return render(request, 'foodie/user_profile.html', context)


@login_required
def save_restaurant(request, restaurant_id):
    '''
    append restaurant id to users save list
    need to make response redirect dynamic on page where list was

    #TODO: dynamically choose user, for now just hard code
    '''
    user = request.user
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    user_restaurant_list_object = get_object_or_404(
        RestaurantList, pk=user.saved_list
    )
    user_restaurant_list = user_restaurant_list_object.restaurant_list
    if restaurant_id not in user_restaurant_list:
        user_restaurant_list.append(restaurant_id)
        user_restaurant_list_object.restaurant_list = user_restaurant_list
        user_restaurant_list_object.save()

        _log_engagement(user, restaurant, 'save')
    else:
        pass

    return redirect('/foodie/recs/saved')


@login_required
def review_restaurant(request, restaurant_id):
    '''
    look into:https://docs.djangoproject.com/en/4.1/topics/forms/
    '''
    user = request.user
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    review = UserRestaurantReview(
        user=user,
        restaurant=restaurant,
        visit_date=request.POST['visit_date'],
        rating=request.POST['rating']
    )
    review.save()
    _log_engagement(user, restaurant, 'review')
    return redirect('/foodie/profile')
