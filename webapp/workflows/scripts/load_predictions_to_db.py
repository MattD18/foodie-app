import sys
sys.path.append("/Users/matthewdalton/Documents/Data Science/Foodie/foodie-app/webapp")

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")

import pandas as pd
from google.cloud import bigquery

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from smsbot.models import Recs
from foodie.models import FoodieUser


# Specify the BigQuery dataset and table you want to read
dataset_id = 'predictions'
table_id = 'user_daily_recs_v2'

if __name__ == '__main__':

    # Create a BigQuery client
    client = bigquery.Client()
    
    # extract from source
    print('--EXTRACT--')
    # Construct the full table reference
    table_ref = client.dataset(dataset_id).table(table_id)
    raw_df = client.query(f'SELECT * FROM `{table_ref}`').to_dataframe()

    # transformation / preprocessing
    print('--TRANSFORM--')
    df = raw_df.copy()

    # load using Django api
    print('--LOAD--')
    num_records_loaded = 0
    for _, record in df.iterrows():
        user = FoodieUser.objects.get(pk=record['user'])
        model_vals = {
            'user': user,
            'restaurant': record['restaurant']
        }
        r = Recs(**model_vals)
        r.save()
        num_records_loaded += 1
    print(num_records_loaded)