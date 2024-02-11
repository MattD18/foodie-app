import os
import datetime
import re

import pandas as pd
from sqlalchemy import create_engine

from google.cloud import bigquery

import environ
import io
from google.cloud import secretmanager


from .models import (
    Restaurant
)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# [START gaestd_py_django_secret_config]
env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, ".env")

if os.path.isfile(env_file):
    # Use a local secret file, if provided
    env.read_env(env_file)
# [START_EXCLUDE]
elif os.getenv("TRAMPOLINE_CI", None):
    # Create local settings if running with CI, for unit testing

    placeholder = (
        f"SECRET_KEY=a\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
# [END_EXCLUDE]
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    env.read_env(io.StringIO(payload))
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")
# [END gaestd_py_django_secret_config]


DATASET_NAME = os.environ.get('WAREHOUSE_DATASET')

TABLE_MAPPING = {
    'dim_restaurant': 'smsbot_restaurant',
    'dim_user': 'smsbot_foodieuser',
    'fct_user_engagement': 'smsbot_engagement',
    'fct_user_conversation': 'smsbot_conversation',
}

SCHEMA_MAPPING = {
    'dim_restaurant': [
        {
            "name": "ds",
            "type": "DATE",
            "mode": "NULLABLE"
        },
        {
            "name": "id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "name",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE"
        },
        {
            "name": "google_maps_url",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "google_maps_id",
            "type": "STRING",
            "mode": "NULLABLE"
        },
    ],
    'dim_user': [
        {
            "name": "ds",
            "type": "DATE",
            "mode": "NULLABLE"
        },
        {
            "name": "id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "phone_number",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "is_staff",
            "type": "BOOL",
            "mode": "NULLABLE"
        },
        {
            "name": "is_active",
            "type": "BOOL",
            "mode": "NULLABLE"
        },
        {
            "name": "date_joined",
            "type": "TIMESTAMP",
            "mode": "NULLABLE"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE"
        },
    ],
    'fct_user_engagement': [
        {
            "name": "ds",
            "type": "DATE",
            "mode": "NULLABLE"
        },
        {
            "name": "id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "user_id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "restaurant_id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "action",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE"
        },
    ],
    'fct_user_conversation': [
        {
            "name": "ds",
            "type": "DATE",
            "mode": "NULLABLE"
        },
        {
            "name": "id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "ts",
            "type": "TIMESTAMP",
            "mode": "NULLABLE"
        },
        {
            "name": "sender",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "message",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "response",
            "type": "STRING",
            "mode": "NULLABLE"
        },

    ],
}


def read_from_postgres(postgres_table, engine):
    df = pd.read_sql_query(
        f'select * from {postgres_table}',
        con=engine
    )
    return df


def upload_to_bq(
    df,
    destination_table,
    table_schema,
    ds,
    project_id,
):
    # add ds partition
    df.insert(loc=0, column='ds', value=ds)
    cols = [col['name'] for col in table_schema]
    # upload table, TODO abstract table_schema to shared location
    df[cols].to_gbq(
        destination_table,
        project_id=project_id,
        if_exists='replace', #TODO: update to insert new partitions instead of overwrite
        table_schema=table_schema
    )


def fix_conn_str(conn_str):
    # Regular expression pattern to match the first "postgres"
    pattern = r'postgres'
    # Replacement string
    replacement = 'postgresql'
    # Replace the first occurrence of "postgres" with "postgressql"
    out_str = re.sub(pattern, replacement, conn_str, count=1)
    return out_str


def upload_app_data_to_bq():
    # establish bigquery connection
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")    # establish postgres connection
    conn_str = os.environ.get("DATABASE_URL")
    conn_str = fix_conn_str(conn_str)
    engine = create_engine(conn_str)
    # grab upload date
    ds = datetime.date.today()
    # upload tables
    for table in TABLE_MAPPING:
        print(f"upload {table}")
        destination_table = f"{DATASET_NAME}.{table}"
        postgres_table = TABLE_MAPPING.get(table)
        # read copy of table from postgres
        df = read_from_postgres(postgres_table, engine)
        # upload to bigquery
        table_schema = SCHEMA_MAPPING.get(table)
        upload_to_bq(
            df,
            destination_table,
            table_schema,
            ds,
            project_id,
        )
    
#TODO: Refactor for new schema
def download_features_from_bq():
    '''
    download restaurant features to server and upload to table
    '''
    pass
#     # establish bigquery connection
#     project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")    # establish postgres connection
#     # pull restaurant features
#     query  = '''
#         SELECT 
#             id,
#             google_maps_rating as ranking_quality_score,
#             neighborhood_id
#         FROM warehouse_features.restaurant_basic_google_maps
#     '''
#     df = pd.read_gbq(query, project_id=project_id)
#     print(df.shape)
#     print(df.head(1))
#     # write features to db
#     for i, record in df.iterrows():
#         restaurant = Restaurant.objects.get(pk=record['id'])
#         try:
#             neighborhood = Neighborhood.objects.get(pk=record['neighborhood_id'])
#         except Neighborhood.DoesNotExist:
#             neighborhood = None
        
#         rf, _ = RestaurantFeatures.objects.update_or_create(
#             restaurant=restaurant,
#             defaults={
#                 'created_at': datetime.datetime.now(),
#                 'ranking_quality_score': record['ranking_quality_score'],
#                 'neighborhood': neighborhood,
#             }
#         )
#         if (i % 500 == 0):
#             print(i)


### Load restaurants from scraper into DB###

# get existing google maps to application mappings
def get_id_mapping_dict():
    
    query = '''

        select
            google_maps_id,
            application_id
        from restaurant_data.restaurant_id_mapping

    '''
    df = pd.read_gbq(query, project_id=project_id)

    id_mapping_dict = dict(zip(df['google_maps_id'], df['application_id']))
    return id_mapping_dict


# get new restauarnts 
def get_google_maps_restaurant_df(ds):
    query = f'''

        SELECT
          name,
          formatted_address as address,
          max_by(place_id, updated_at) as google_maps_id,
          max_by(url, updated_at) as google_maps_url
        FROM `foodie-355420.restaurant_data.google_maps_place_logs`
        where updated_at >= '{ds}'
        group by 1, 2

    '''
    
    df = pd.read_gbq(query, project_id=project_id)

    return df

def download_restaurants_from_bq():
    
    
    # get current mapping
    id_mapping_dict = get_id_mapping_dict()
    # get new restuarants to upload
    ds = (datetime.datetime.today() - datetime.timedelta(2)).strftime("%Y-%m-%d")
    google_maps_restaurant_df = get_google_maps_restaurant_df(ds=ds)
    
    new_restaurant_ids = {}
    num_new_restaurants = 0
    num_updated_restaurants = 0
    # iterate through restaurnts, look for id match
    for i, record in google_maps_restaurant_df.iterrows():
        restaurant = Restaurant.objects.filter(name=record['name'], address=record['address'])
        gid = record['google_maps_id']
        if len(restaurant) > 0:
            restaurant = restaurant[0]

            # add new id pairing if needed
            if id_mapping_dict.get(gid) != restaurant.id:
                new_restaurant_ids[gid] = restaurant.id
                num_updated_restaurants += 1
        else:
            # add restaurant to db
            fields = {
                'name': record['name'],
                'address': record['address'],
                'google_maps_url': record['google_maps_url'],
                'created_at': datetime.datetime.now(),
            }
            r = Restaurant(**fields)
            r.save()
            # add google_maps_id_mapping
            new_restaurant_ids[gid] = r.id
            num_new_restaurants += 1

    # upload refreshed mapping
    data = { 
        'google_maps_id':new_restaurant_ids.keys(),   
        'application_id':new_restaurant_ids.values()
    }
    upload_df = pd.DataFrame(data)
    table_schema = [
        {
            "name": "google_maps_id",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "application_id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
    ]
    destination_table = 'restaurant_data.restaurant_id_mapping'

    upload_df.to_gbq(
        destination_table,
        project_id=project_id,
        if_exists='append',
        table_schema=table_schema
    )