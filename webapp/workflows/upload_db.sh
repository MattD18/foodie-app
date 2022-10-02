# upload app db to bq
cp workflows/scripts/upload_app_data_to_bq.py upload_app_data_to_bq.py
python upload_app_data_to_bq.py
rm upload_app_data_to_bq.py