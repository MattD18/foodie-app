import re
import datetime
import pandas as pd
from sqlalchemy import create_engine

from .config import TABLE_MAPPING, SCHEMA_MAPPING, DATASET_NAME


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

def upload_app_data_to_bq(project_id, engine):
    # establish bigquery connection
    
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