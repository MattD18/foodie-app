from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .forms import FoodieUserCreationForm, FoodieUserChangeForm
from .models import Restaurant, RestaurantList, FoodieUser, Engagement




class FoodieUserAdmin(UserAdmin):
    add_form = FoodieUserCreationForm
    form = FoodieUserChangeForm
    model = FoodieUser
    list_display = ('phone_number', 'is_staff', 'is_active',)
    list_filter = ('phone_number', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)


admin.site.register(FoodieUser, FoodieUserAdmin)

admin.site.register(Restaurant)
admin.site.register(RestaurantList)
admin.site.register(Engagement)
