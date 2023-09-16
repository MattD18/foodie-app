import sys
sys.path.append("/Users/matthewdalton/Documents/Data Science/Foodie/foodie-app/webapp")

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")

import pandas as pd

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from foodie.models import Restaurant, RestaurantList


# Purpose - to be run on db set-up to first load in restaurants
# local source is temp, can replace with different ingestion method
DATA_SOURCE_PATH = 'data/google_maps_restaurants.csv'

COLUMN_MAPPINGS = {
 'name': 'name'
}





if __name__ == '__main__':

    # extract from source
    print('--EXTRACT--')
    df = pd.read_csv(DATA_SOURCE_PATH)
    print(df.shape)

    # transformation / preprocessing
    print('--TRANSFORM--')
    #df = df.head()
    print(df.shape)
    # load using Django api
    print('--LOAD--')
    num_records_loaded = 0
    for _, record in df.iterrows():
        # TODO: Add checker
        model_vals = {
            attribute: record[COLUMN_MAPPINGS.get(attribute)] for attribute in COLUMN_MAPPINGS
        }
        r = Restaurant(**model_vals)
        r.save()
        num_records_loaded += 1
    print(num_records_loaded)

    # check for existence of default reclist
    # else: create default reclist

    if len(RestaurantList.objects.all()) == 0:
        rl = RestaurantList(
            name='Daily Picks For You',
            restaurant_list=[1, 2, 3, 4, 5],
        )
        rl.save()
        print('creating default rec list')
