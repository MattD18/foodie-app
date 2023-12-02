# Third-party imports
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import numpy as np

# Internal imports
from .models import Restaurant, Conversation
from .utils import send_message, logger, log_engagement, create_new_user
from .data_transfer import upload_app_data_to_bq, download_features_from_bq
from .rec_engine import RecEngine

def index(request):
    return HttpResponse("Hello world, it's Foodie")


@csrf_exempt
@login_required(login_url="/smsbot/login/")
def reply(request):
    # Extract the phone number from the incoming webhook request
    phone_number = request.POST.get('From').split("phone:")[-1]
    print(f"Sending the response to this number: {phone_number}")
    # get user message
    body = request.POST.get('Body', '')
    # Retrieve the author
    user = request.user

    # classify intent
    intent = 'fallback'
    if 'Rec me' in body:
        intent = 'recommendation'

        # formulate response
        if intent == 'recommendation':
            # Generate a restaurant recommendation
            rec_engine = RecEngine()
            query = body
            rec = rec_engine.get_recommendation(query)
            if rec is None:
                response = 'No recs found. Text "Rec me" to receive our restaurant pick for you\n\nOr try "Rec me <neighborhood>" to search a specifc area, for example "Rec me Williamsburg"'
            else:
                restaurant = Restaurant.objects.get(id=rec)
                if restaurant is not None:
                    response = f'Our rec for you is {restaurant.name}: \n\n{restaurant.google_maps_url}'
                else:
                    response = 'No recs found. Text "Rec me" to receive our restaurant pick for you\n\nOr try "Rec me <neighborhood>" to search a specifc area, for example "Rec me Williamsburg"'
    else:
        response = 'Text "Rec me" to receive our restaurant pick for you\n\nOr try "Rec me <neighborhood>" to search a specifc area, for example "Rec me Williamsburg"'

    # send response
    send_message(phone_number, response)

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

    # log sms impression
    if intent == 'recommendation':
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


def upload_warehouse(request):
    '''
    Cron job reference: https://github.com/sungchun12/schedule-python-script-using-Google-Cloud/tree/master/chicago_traffic
    '''

    is_cron = request.headers.get('X-Appengine-Cron', False)
    if not is_cron:
        return HttpResponseBadRequest()
    upload_app_data_to_bq()
    return HttpResponse('')


def download_features(request):
    '''
    Cron job reference: https://github.com/sungchun12/schedule-python-script-using-Google-Cloud/tree/master/chicago_traffic
    '''

    is_cron = request.headers.get('X-Appengine-Cron', False)
    if not is_cron:
        return HttpResponseBadRequest()
    download_features_from_bq()
    return HttpResponse('')
