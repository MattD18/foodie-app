import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodie.settings")

import django
# Initialize Django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.core.wsgi import get_wsgi_application

from smsbot.models import Neighborhood

import pandas as pd


# Purpose - to be run on db set-up to first load in restaurants
# local source is temp, can replace with different ingestion method
DATA_SOURCE_PATH = 'local_data/neighborhoods.csv'
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
    assert len(Neighborhood.objects.all()) == 0
    for _, record in df.iterrows():
        # TODO: Add checker
        fields = {
            'name': record['name'],
            'borough': record['borough']
        }
        # assumes neighborhoods are properly sorted for id matching
        n = Neighborhood(**fields)
        n.save()
        num_records_loaded += 1
    print(num_records_loaded)