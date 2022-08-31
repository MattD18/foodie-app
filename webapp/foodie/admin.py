from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import Restaurant, RestaurantList, User

admin.site.register(Restaurant)
admin.site.register(RestaurantList)
admin.site.register(User, UserAdmin)
