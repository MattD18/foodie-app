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
    google_maps_url = models.URLField(max_length=200, null=True)
    google_maps_id = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return self.name


class Neighborhood(models.Model):
    '''
    Neighborhoods
    '''
    name = models.CharField(max_length=200)
    borough = models.CharField(max_length=200)


class Engagement(models.Model):
    '''
    used to log interactions such as impressions
    '''
    LOG_ACTIONS = (
        ('sms_impression', 'User sent restaurant via sms'),
    )
    user = models.ForeignKey(FoodieUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=LOG_ACTIONS)
    created_at = models.DateTimeField(auto_now_add=True)


# Create your models here.
class Conversation(models.Model):
    '''
    converation with user
    '''
    ts = models.DateTimeField(auto_now_add=True, blank=True)
    sender = models.CharField(max_length=15)
    message = models.CharField(max_length=2000)
    response = models.CharField(max_length=2000)


class RestaurantFeatures(models.Model):
    '''
    Restaurant features used for recommender system
    '''
    restaurant = models.OneToOneField(Restaurant, primary_key=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    ranking_quality_score = models.FloatField()
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, null=True)
