from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
from django.db import models

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

class User(AbstractUser):
    '''
    '''
    user_restaurant_list = models.IntegerField()