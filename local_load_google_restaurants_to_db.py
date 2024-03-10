import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodie.settings")

import django
# Initialize Django
django.setup()

from django.core.wsgi import get_wsgi_application


from smsbot.data_transfer import download_restaurants_from_bq, upload_app_data_to_bq


# Purpose - to be run on db set-up to first load in restaurants
if __name__ == '__main__':
    download_restaurants_from_bq(ds='2024-01-06')
    upload_app_data_to_bq()