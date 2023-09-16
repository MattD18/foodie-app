import sys
sys.path.append("/home/mattgeorgedalton/foodie-app/webapp")

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")

import pandas as pd

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from foodie.models import Restaurant, RestaurantList


# Purpose - to be run on db set-up to first load in restaurants
# local source is temp, can replace with different ingestion method
DATA_SOURCE_PATH = 'data/personal_recs_two.csv'

COLUMN_MAPPINGS = {
 'neighborhood': 'neighborhood',
 'name': 'name',
 'address': 'street_address',
 'zipcode': 'zipcode',
 'cuisine': 'cuisine',
 'tags': 'tags',
 'price_est': 'est_price_per_person',
 'website_url': 'website_url',
 'menu_url': 'menu_url',
}


class RestaurantChecker():

    def check_restaurant_exists(self, record):
        exists = False
        name = record[COLUMN_MAPPINGS.get('name')]
        address = record[COLUMN_MAPPINGS.get('address')]
        restaurant_candidates = Restaurant.objects.filter(name=name)
        for restaurant in restaurant_candidates:
            if restaurant.address == address:
                exists = True
        return exists


if __name__ == '__main__':

    # initialize restaurant checker
    checker = RestaurantChecker()

    # extract from source
    print('--EXTRACT--')
    df = pd.read_csv(DATA_SOURCE_PATH)
    print(df.shape)

    # transformation / preprocessing
    print('--TRANSFORM--')
    #df = df.head()
    df.columns = [col.lower().replace(' ', '_') for col in  df.columns]
    df['zipcode'] = df['zipcode'].astype(int)
    df['tags'] = df['tags'].apply(lambda x: x.split(','))
    df['est_price_per_person'] = df['est_price_per_person'].astype(int).astype(str)
    print(df.shape)
    # load using Django api
    print('--LOAD--')
    num_records_loaded = 0
    for _, record in df.iterrows():
        # check against name for now
        restaurant_exists = checker.check_restaurant_exists(record)
        if not restaurant_exists:
            model_vals = {
                attribute: record[COLUMN_MAPPINGS.get(attribute)] for attribute in COLUMN_MAPPINGS
            }
            r = Restaurant(**model_vals)
            r.save()
            num_records_loaded += 1
        else:
            restaurant_name = record[COLUMN_MAPPINGS.get('name')]
            print(f'skipping {restaurant_name}')
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
