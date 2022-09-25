from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import FoodieUser


class FoodieUserCreationForm(UserCreationForm):

    class Meta:
        model = FoodieUser
        fields = ('phone_number',)


class FoodieUserChangeForm(UserChangeForm):

    class Meta:
        model = FoodieUser
        fields = ('phone_number',)
