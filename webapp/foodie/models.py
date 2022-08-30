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