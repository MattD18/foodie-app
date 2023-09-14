# Third-party imports
from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

# Internal imports
from .models import Conversation, Recs
from foodie.models import FoodieUser
from .utils import send_message, logger

def index(request):
    return HttpResponse("Hello")


@csrf_exempt
def reply(request):
    # Extract the phone number from the incoming webhook request
    phone_number = request.POST.get('From').split("phone:")[-1]
    print(f"Sending the response to this number: {phone_number}")

    body = request.POST.get('Body', '')
    # Retrieve the author
    user = FoodieUser.objects.get(pk=1)
    rec = Recs.objects.filter(user=user)
    rec = list(rec)[0].restaurant
    response = f'Our rec of the day is {rec}'

    # Store the conversation in the database
    try:

        with transaction.atomic():
                conversation = Conversation.objects.create(
                    sender=phone_number,
                    message=body,
                    response=response
                )
                conversation.save()
                logger.info(f"Conversation #{conversation.id} stored in database")
    except Exception as e:
        logger.error(f"Error storing conversation in database: {e}")
        return HttpResponse(status=500)

    send_message(phone_number, response)
    return HttpResponse('')
