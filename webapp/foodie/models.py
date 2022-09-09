from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import FoodieUserManager


# Create your models here.
class FoodieUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(unique=True, max_length=12)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    foodie_username = models.CharField(max_length=20, blank=True)
    # TODO figure out fk relationship
    saved_list = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = FoodieUserManager()

    def __str__(self):
        return self.foodie_username


class Restaurant(models.Model):
    '''
    attributes should be useful to user first
    should be useful to rec system second
    attributes can be modifiable from UI + backend
    '''
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    neighborhood = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=200)
    tags = ArrayField(
        models.CharField(max_length=200)
    )
    price_range = models.CharField(max_length=200)
    website_url = models.URLField(max_length=200)
    menu_url = models.URLField(max_length=200)
    # fields to add then migrate:
    # avg_user_rating
    # image url

    def __str__(self):
        return self.name


class RestaurantList(models.Model):
    '''
    List of restaurants
    '''
    name = models.CharField(max_length=200)
    restaurant_list = ArrayField(
        models.IntegerField(),  # TODO figure out fk relationship
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(FoodieUser, on_delete=models.CASCADE),

    def __str__(self):
        return self.name


class UserRecList(models.Model):
    '''
    list to serve to logged in user when visiting foodie/recs/ page
    '''
    user = models.ForeignKey(FoodieUser, on_delete=models.CASCADE)
    restaurant_list = models.ForeignKey(
        RestaurantList,
        on_delete=models.CASCADE
    )

class UserRestaurantRating(models.Model):
    '''
    consider adding timestamp of rating
    '''
    user = models.ForeignKey(FoodieUser,  on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rating = models.IntegerField()


class UserRestaurantVisit(models.Model):
    '''
    eventually ties rating to visit, can only rate once they have visited
    '''
    user = models.ForeignKey(FoodieUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    review = models.CharField(max_length=200)


class Engagement(models.Model):
    '''
    used to log interactions such as impressions, likes, saves
    consider turning engagement objects into own models as well
        to log data such as origin list id for saved / impressions events
    visit should be own model to store detail about visit (reviews, timing)
    '''
    LOG_ACTIONS = (
        ('rate', 'User rates restaurant'),
        ('visit', 'User reports visiting restaurant'),
        ('save', 'User saved restaurant'),
        ('impression', 'User shown restaurant'),
    )
    user = models.ForeignKey(FoodieUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=LOG_ACTIONS)
    created_at = models.DateTimeField(auto_now_add=True)
