# Third-party imports
from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import numpy as np

# Internal imports
from .models import FoodieUser, Restaurant, Engagement, Conversation
from .utils import send_message, logger, log_engagement, create_new_user

def index(request):
    return HttpResponse("Hello")

@csrf_exempt
@login_required(login_url="/smsbot/login/")
def reply(request):
    # Extract the phone number from the incoming webhook request
    phone_number = request.POST.get('From').split("phone:")[-1]
    print(f"Sending the response to this number: {phone_number}")

    body = request.POST.get('Body', '')
    # Retrieve the author
    user = request.user

    # Generate a restaurant recommendation (default rec is random)
    restaurant = np.random.choice(Restaurant.objects.all())
    # response = f'Our rec for you is {restaurant.name}. \nLink: {restaurant.google_maps_url} \nFor more recs, text \"Rec me\"'
    response = f'Our rec for you is {restaurant.name}.\n\nFor more recs, text \"Rec me\"'
  
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
    # log sms impression
    log_engagement(user, restaurant, 'sms_impression')

    return HttpResponse('')

@csrf_exempt
def sms_login(request):
    phone_number = request.POST.get('From').split("phone:")[-1]
    user = authenticate(request, phone_number=phone_number)
    if user is not None:
        login(request, user)
    else:
        new_user = create_new_user(phone_number=phone_number)
        login(request, new_user)
        # TODO: for new users redirect to onboarding flow
    return redirect('/smsbot/message/')