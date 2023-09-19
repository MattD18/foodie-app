import sys
sys.path.append("/home/mattgeorgedalton/foodie-app/webapp")

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")

import pandas as pd
from google.cloud import bigquery

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from smsbot.models import Recs
from foodie.models import FoodieUser, Restaurant


# Specify the BigQuery dataset and table you want to read
dataset_id = 'inference'
table_id = 'sms_daily_rec_predictions'

if __name__ == '__main__':

    # Create a BigQuery client
    client = bigquery.Client()
    
    # extract from source
    print('--EXTRACT--')
    # Construct the full table reference
    table_ref = client.dataset(dataset_id).table(table_id)
    query = f'''
    
    SELECT 
        max(ts) as ts,
        user,
        max_by(restaurant_id, ts) as restaurant_id,
        max_by(name, ts) as restaurant_name
    FROM `{table_ref}`
    group by 1
    '''
    raw_df = client.query(f'SELECT * FROM `{table_ref}`').to_dataframe()

    # transformation / preprocessing
    print('--TRANSFORM--')
    df = raw_df.copy()

    # load using Django api
    print('--LOAD--')
    num_records_loaded = 0
    for _, record in df.iterrows():
        user = FoodieUser.objects.get(pk=record['user'])
        print(record['restaurant_id'])
        restaurant = Restaurant.objects.get(pk=int(record['restaurant_id']))
        print(restaurant.name)
        model_vals = {
            'ts': record['ts'],
            'user': user,
            'restaurant': restaurant
        }
        r = Recs(**model_vals)
        r.save()
        num_records_loaded += 1
    print(num_records_loaded)
