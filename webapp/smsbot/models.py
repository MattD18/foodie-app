from django.db import models
from foodie.models import FoodieUser, Restaurant

# Create your models here.
class Conversation(models.Model):
    sender = models.CharField(max_length=15)
    message = models.CharField(max_length=2000)
    response = models.CharField(max_length=2000)

# Create your models here.
class Recs(models.Model):
    '''
    daily recs from prediction service for each user
    '''
    ts = models.DateTimeField()
    user = models.ForeignKey(FoodieUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)


