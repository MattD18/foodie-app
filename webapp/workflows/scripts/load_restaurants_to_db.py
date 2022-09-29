
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")

import pandas as pd

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from foodie.models import Restaurant, RestaurantList


# Purpose - to be run on db set-up to first load in restaurants
# local source is temp, can replace with different ingestion method
DATA_SOURCE_PATH = 'data/personal_recs.csv'

COLUMN_MAPPINGS = {
 'neighborhood': 'neighborhood',
 'name': 'name',
 'address': 'street_address',
 'zipcode': 'zipcode',
 'cuisine': 'cuisine',
 'tags': 'tags',
 'price_est': 'median_entree_price',
 'website_url': 'website_url',
 'menu_url': 'menu_url',
}


if __name__ == '__main__':

    # extract from source
    print('--EXTRACT--')
    df = pd.read_csv(DATA_SOURCE_PATH)
    print(df.shape)

    # transformation / preprocessing
    print('--TRANSFORM--')
    df = df.head()
    df.columns = [col.lower().replace(' ', '_') for col in  df.columns]
    df['zipcode'] = df['zipcode'].astype(int)
    df['tags'] = df['tags'].apply(lambda x: x.split(','))
    df['median_entree_price'] = df['median_entree_price'].astype(int).astype(str)
    print(df.shape)
    # load using Django api
    print('--LOAD--')
    num_records_loaded = 0
    for _, record in df.iterrows():
        if not Restaurant.objects.filter(name=record[COLUMN_MAPPINGS.get('name')]):
            model_vals = {
                attribute: record[COLUMN_MAPPINGS.get(attribute)] for attribute in COLUMN_MAPPINGS
            }
            r = Restaurant(**model_vals)
            r.save()
            num_records_loaded += 1
    print(num_records_loaded)

    # create default reclist
    rl = RestaurantList(
        name='Daily Picks For You',
        restaurant_list=[1, 2, 3, 4, 5],
    )
    rl.save()
    print('creating default rec list')
