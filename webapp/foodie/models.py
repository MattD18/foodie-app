from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import FoodieUserManager

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    # fields to add then migrate:
        # user_rating
        # address
        # cuisine tags
        # image url?

    def __str__(self):
        return self.name


class RestaurantList(models.Model):
    '''
    List of restaurants
    '''
    name = models.CharField(max_length=200)
    restaurant_list = ArrayField(
        models.IntegerField(),
    )

    def __str__(self):
        return self.name

class FoodieUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(unique=True, max_length=12)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    foodie_username =  models.CharField(max_length=20, blank=True)
    saved_list = models.IntegerField(null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = FoodieUserManager()

    def __str__(self):
        return self.foodie_username