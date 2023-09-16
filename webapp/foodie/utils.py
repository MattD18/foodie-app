
from .models import (
    RestaurantList,
    FoodieUser,
    Engagement,
    UserRecList,
)

def log_engagement(user, restaurant, engagement_type):
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


def create_new_user(phone_number):
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