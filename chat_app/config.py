TABLE_MAPPING = {
    'dim_restaurant': 'smsbot_restaurant',
    'dim_user': 'smsbot_foodieuser',
    'dim_place': 'smsbot_place',
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
            "name": "address",
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
            "name": "ranking_quality_score",
            "type": "FLOAT",
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
    'dim_place': [
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
            "name": "geo",
            "type": "STRING",
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

DATASET_NAME = 'application_prod'