import re
import datetime
import pandas as pd
from sqlalchemy import create_engine

from .config import TABLE_MAPPING, SCHEMA_MAPPING
from . import models, schemas, crud

def fix_conn_str(conn_str):
    # Regular expression pattern to match the first "postgres"
    pattern = r'postgres'
    # Replacement string
    replacement = 'postgresql'
    # Replace the first occurrence of "postgres" with "postgressql"
    out_str = re.sub(pattern, replacement, conn_str, count=1)
    return out_str

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

def upload_app_data_to_bq(project_id, dataset, engine):
    # grab upload date
    ds = datetime.date.today()
    # upload tables
    for table in TABLE_MAPPING:
        print(f"upload {table}")
        destination_table = f"{dataset}.{table}"
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

# get existing google maps to application mappings
def get_id_mapping_dict(project_id, prod_flag):
    
    if prod_flag:
        id_mapping_table = 'restaurant_data.restaurant_id_mapping'
    else:
        id_mapping_table = 'restaurant_data.restaurant_id_mapping_test'

    query = f'''

        select
            google_maps_id,
            application_id
        from {id_mapping_table}

    '''
    
    df = pd.read_gbq(query, project_id=project_id)
    id_mapping_dict = dict(zip(df['google_maps_id'], df['application_id']))
    return id_mapping_dict


# get new restauarnts 
def get_google_maps_restaurant_df(ds, project_id):
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


def download_restaurants_from_bq(db, ds, project_id, prod_flag):
    

    # get current mapping
    id_mapping_dict = get_id_mapping_dict(project_id=project_id, prod_flag=prod_flag)
    # get new restuarants to upload
    google_maps_restaurant_df = get_google_maps_restaurant_df(ds=ds, project_id=project_id)
    
    new_restaurant_ids = {}
    num_new_restaurants = 0
    num_updated_restaurants = 0
    # iterate through restaurnts, look for id match
    for i, record in google_maps_restaurant_df.iterrows():
       
        restaurant =  db.query(models.Restaurant) \
            .filter(
                models.Restaurant.name == record['name'], 
                models.Restaurant.address == record['address']
        ).first()
        gid = record['google_maps_id']
        if restaurant is not None:
            # add new id pairing if needed
            if id_mapping_dict.get(gid) != restaurant.id:
                new_restaurant_ids[gid] = restaurant.id
                num_updated_restaurants += 1
        else:
            # add restaurant to db
            restaurant = schemas.RestaurantCreate(
                name = record['name'],
                address = record['address'],
                google_maps_url = record['google_maps_url'],
                created_at = datetime.datetime.now()
            )
            crud.create_restaurant(db=db, restaurant=restaurant)
            restaurant =  db.query(models.Restaurant) \
                .filter(
                    models.Restaurant.name == record['name'], 
                    models.Restaurant.address == record['address']
            ).first()

            # add google_maps_id_mapping
            new_restaurant_ids[gid] = restaurant.id
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

    if prod_flag:
        id_mapping_table = 'restaurant_data.restaurant_id_mapping'
    else:
        id_mapping_table = 'restaurant_data.restaurant_id_mapping_test'

    destination_table = id_mapping_table

    upload_df.to_gbq(
        destination_table,
        project_id=project_id,
        if_exists='append',
        table_schema=table_schema
    )


def download_features_from_bq(db, project_id):
    '''
    download restaurant features to server and upload to table
    '''
    # pull restaurant features
    query  = '''
        SELECT 
            id,
            ranking_quality_score,
            place_tags
        FROM warehouse_features.restaurant_basic_google_maps_v2
    '''
    df = pd.read_gbq(query, project_id=project_id)
    print(df.shape)
    print(df.head(1))
    # write features to db
    for i, record in df.iterrows():

        db_restaurant = db.query(models.Restaurant) \
            .filter(
                models.Restaurant.id == record['id'], 
        ).first()
        if db_restaurant:
            # Update the fields
            db_restaurant.ranking_quality_score = record['ranking_quality_score']

            if len(record['place_tags']) > 0:
                place_tags = [int(x) for x in record['place_tags']]
                db_restaurant.places = db.query(models.Place).filter(
                    models.Place.id.in_(place_tags)
                ).all()
            db.commit()
        if (i % 500 == 0):
            print(i)