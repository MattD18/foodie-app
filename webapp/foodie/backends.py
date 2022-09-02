from django.conf import settings
from django.contrib.auth.hashers import check_password
from foodie.models import FoodieUser

class FoodieBackend(object):
    """
    Authenticate user
    """

    def authenticate(self, request, phone_number):
        try:
            return FoodieUser.objects.get(phone_number=phone_number)
        except FoodieUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return FoodieUser.objects.get(pk=user_id)
        except FoodieUser.DoesNotExist:
            return None