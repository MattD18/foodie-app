# Standard library import
import logging
import os

# Third-party imports
from twilio.rest import Client

from .models import (
    FoodieUser,
    Engagement,
)

def log_engagement(user, restaurant, engagement_type):
    '''
    log result in engagement as well
    '''
    e = Engagement(
        user=user,
        restaurant=restaurant,
        action=engagement_type
    )
    e.save()
    return


def create_new_user(phone_number):
    u = FoodieUser(
        phone_number=phone_number,
    )
    u.save()
    return u



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)
twilio_number = os.environ['TWILIO_NUMBER']

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=twilio_number,
            body=body_text,
            to=to_number
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")