import os
import datetime

import pandas as pd
from sqlalchemy import create_engine

from google.cloud import bigquery

dataset_name = 'demo_data'

table_mapping = {
    'dim_restaurant': 'foodie_restaurant',
    'dim_user': 'foodie_foodieuser',
    'fct_user_engagement': 'foodie_engagement',
}

schema_mapping = {
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
            "name": "address",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "zipcode",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "neighborhood",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "cuisine",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "tags",
            "type": "STRING",
            "mode": "REPEATED"
        },
        {
            "name": "price_est",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "website_url",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "menu_url",
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
            "name": "neighborhood",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "saved_list",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "last_login",
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
            "name": "action",
            "type": "STRING",
            "mode": "NULLABLE"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE"
        },
        {
            "name": "restaurant_id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
        {
            "name": "user_id",
            "type": "INTEGER",
            "mode": "NULLABLE"
        },
    ],
}


def check_partition(table_name, ds):
    exist_flag = False
    table_check_query = f"""
        select
            max(ds)
        from {table_name}
    """
    table_check = bq_client.query(query=table_check_query).to_dataframe()
    exist_flag = table_check.iloc[0][0] == ds
    return exist_flag


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
        if_exists='append',
        table_schema=table_schema
    )


if __name__ == '__main__':

    # establish bigquery connection
    project_id = os.environ['GCP_PROJECT']
    bq_client = bigquery.Client(project=project_id)
    # establish postgres connection
    conn_str = 'postgresql://foodielocal:foodie@localhost:5432/foodiedb'
    engine = create_engine(conn_str)
    # grab upload date
    ds = datetime.date.today()
    # upload tables
    for table in table_mapping:
        print(f"upload {table}")
        destination_table = f"{dataset_name}.{table}"
        # check that partition doesn't exist for day
        # in future, need to figure out how to overwrite partition
        partition_exist = check_partition(destination_table, ds)
        if not partition_exist:
            # read copy of table from postgres
            postgres_table = table_mapping.get(table)
            df = read_from_postgres(postgres_table, engine)
            # upload to bigquery
            table_schema = schema_mapping.get(table)
            upload_to_bq(
                df,
                destination_table,
                table_schema,
                ds,
                project_id,
            )
            print(f"uploaded {ds} partition for {table}")
        else:
            print(f"{ds} partition exists for {table}")
