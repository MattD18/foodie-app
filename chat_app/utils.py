import os
import tempfile

from google.cloud import secretmanager
from dotenv import dotenv_values

def get_env_vars():
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(BASE_DIR, ".env")

    if os.path.isfile(env_file):
        # Load environment variables from .env file for testing
        env_vars = dotenv_values(env_file)
    else:
    # Pull secrets from Secret Manager
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        client = secretmanager.SecretManagerServiceClient()
        settings_name = os.environ.get("SETTINGS_NAME", "fast_api_settings")
        name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
        payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
        # Write the environment variables to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(payload)
            temp_file_path = temp_file.name
        # Load environment variables from the temporary file
        env_vars = dotenv_values(temp_file_path)
    return env_vars