import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodie.settings")

from django.core.wsgi import get_wsgi_application
from django.core.wsgi import get_wsgi_application

from smsbot.models import Restaurant


import pandas as pd


# Purpose - to be run on db set-up to first load in restaurants
# local source is temp, can replace with different ingestion method
DATA_SOURCE_PATH = 'local_data/google_restaurant_data.csv'
DATABASE = os.environ['DATABASE_URL']


if __name__ == '__main__':
    # CHECK DATABASE
    print(DATABASE)
    # extract from source
    print('--EXTRACT--')
    df = pd.read_csv(DATA_SOURCE_PATH)
    print(df.shape)
    print(df.head())

    # transformation / preprocessing
    print('--TRANSFORM--')
    print(df.shape)

    # load using Django api
    print('--LOAD--')
    num_records_loaded = 0
    # only use to update empty database for now, TODO figure out incremental updates
    assert len(Restaurant.objects.all()) == 0
    for _, record in df.iterrows():
        # TODO: Add checker
        fields = {
            'name': record['name'],
            'created_at': record['created_at'],
            'google_maps_url': record['google_maps_url'],
            'google_maps_id': record['google_maps_id'],
        }
        r = Restaurant(**fields)
        r.save()
        num_records_loaded += 1
    print(num_records_loaded)