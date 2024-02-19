import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodie.settings")

import django
# Initialize Django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.core.wsgi import get_wsgi_application

from smsbot.models import Place

import pandas as pd


DATA_SOURCE_PATH = 'local_data/nyc_neighborhood_places.csv'
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
    assert len(Place.objects.all()) == 0
    for _, record in df.iterrows():
        # TODO: Add checker
        fields = {
            'name': record['name'],
            'geo': record['geo']
        }
        # assumes neighborhoods are properly sorted for id matching
        n = Place(**fields)
        n.save()
        num_records_loaded += 1
    print(num_records_loaded)