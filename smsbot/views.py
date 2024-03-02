# Third-party imports
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import numpy as np

# Internal imports
from .models import Restaurant, Conversation, Place
from .utils import send_message, logger, log_engagement, create_new_user
from .data_transfer import (
    upload_app_data_to_bq, 
    download_features_from_bq,
    download_restaurants_from_bq,
)
from .rec_engine import RecEngine
from .query_parser import QueryParser

def index(request):
    return HttpResponse("Hello world, it's Foodie")


@csrf_exempt
@login_required(login_url="/smsbot/login/")
def reply(request):
    # Extract the phone number from the incoming webhook request
    phone_number = request.POST.get('From').split("phone:")[-1]
    print(f"Sending the response to this number: {phone_number}")
    # get user message
    query_parser = QueryParser()
    user_query = request.POST.get('Body', '')
    user_intent = query_parser.classify_intent(user_query)
    # Retrieve the author
    user = request.user

    # process user query
    if user_intent == 'RECOMMENDATION':
        # Generate a restaurant recommendation
        rec_engine = RecEngine()
        place_id = query_parser.extract_place(user_query)
        rec, query_status = rec_engine.get_recommendation(place_id)
        if query_status == 'NOT_FOUND':
            response = 'No recs found. Try another neighborhood, for example "Rec me Williamsburg"'
        else:
            restaurant = Restaurant.objects.get(id=rec)
            place = Place.objects.get(id=place_id)
            response = f'Our rec for {place.name} is {restaurant.name}: \n\n{restaurant.google_maps_url}'
    elif user_intent == 'FALLBACK':
        response = 'Text "Rec me <neighborhood>" for a local NYC food recommendation, for example: "Rec me Williamsburg"'
    else:
        pass

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
    if user_intent == 'RECOMMENDATION':
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

def download_restaurants(request):
    '''
    Cron job reference: https://github.com/sungchun12/schedule-python-script-using-Google-Cloud/tree/master/chicago_traffic
    '''

    is_cron = request.headers.get('X-Appengine-Cron', False)
    if not is_cron:
        return HttpResponseBadRequest()
    download_restaurants_from_bq()
    return HttpResponse('')