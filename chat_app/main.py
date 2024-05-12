from typing import List
import datetime

from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    Form, 
    Response,
    Request, 
    HTTPException
)

from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from . import crud, models, schemas, utils
from .database import SessionLocal, engine as ENGINE

from .query_parser import QueryParser
from .rec_engine import RecEngine
from .data_transfer import (
    upload_app_data_to_bq, 
    download_restaurants_from_bq,
    download_features_from_bq,
)

from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator  

env_vars = utils.get_env_vars()
PROJECT_ID = env_vars['GOOGLE_CLOUD_PROJECT']
DATASET_NAME = env_vars['WAREHOUSE_DATASET']
PROD_FLAG = env_vars['WAREHOUSE_DATASET'] == 'application_prod'

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user.id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db=db, user=user)



@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/restaurant/{restaurant_id}", response_model=schemas.Restaurant)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    return restaurant

@app.post("/hook")
async def chat(
    request: Request, From: str = Form(...), Body: str = Form(...),
    db: Session = Depends(get_db)
):
    #TODO: use proper validator
    # https://www.twilio.com/docs/usage/webhooks/webhooks-security
    is_twilio = request.headers.get("X-Twilio-Signature", False)
    if not is_twilio:
        raise HTTPException(status_code=400, detail="Error in Twilio Signature")

    # extract message data
    phone_number = From
    user_query = Body
    print(f"Sending the response to this number: {phone_number}")

    #get user
    user = crud.get_user_by_phone_number(db=db, phone_number=phone_number)
    if user is None:
        user = schemas.UserCreate(
            password= "",
            last_login= datetime.datetime.now(),
            is_superuser= False,
            phone_number=phone_number,
            is_staff= False,
            is_active= True,
            date_joined=datetime.datetime.now(),
            created_at= datetime.datetime.now()
        )
        crud.create_user(db=db, user=user)
        user = crud.get_user_by_phone_number(db=db, phone_number=phone_number)
    print(f"User: {user.id}")

    # classify query intent
    qp = QueryParser(db=db)
    user_intent = qp.classify_intent(user_query)

     # # process user query
    log_impression_flag = False
    if user_intent == 'RECOMMENDATION':
        # Generate a restaurant recommendation
        rec_engine = RecEngine(db=db)
        place_id = qp.extract_place(user_query)
        print(place_id)
        query_parameters = {
            'place_id':place_id
        }
        rec, query_status = rec_engine.get_recommendation(query_parameters)
        if (query_status == 'NOT_FOUND') or (place_id is None):
            response_body = 'No recs found. Try another neighborhood, for example "Rec me Williamsburg"'
        else:
            restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == rec).first()
            place = db.query(models.Place).filter(models.Place.id == place_id).first()
            response_body = f'Our rec for {place.name} is {restaurant.name}: \n\n{restaurant.google_maps_url}'
            log_impression_flag = True
    elif user_intent == 'FALLBACK':
        response_body = 'Text "Rec me <neighborhood>" for a local NYC food recommendation, for example: "Rec me Williamsburg"'
    else:
        response_body = 'Text "Rec me <neighborhood>" for a local NYC food recommendation, for example: "Rec me Williamsburg"'


    response = MessagingResponse()
    msg = response.message(response_body)

    #log conversation in db
    if log_impression_flag:
        engagement = schemas.EngagementCreate(
            action="sms_impression",
            created_at= datetime.datetime.now(),
            restaurant_id=restaurant.id,
            user_id=user.id,
        )
        crud.create_engagement(db=db, engagement=engagement)
    

    conversation = schemas.ConversationCreate(
            ts=datetime.datetime.now(),
            sender=phone_number,
            message=user_query,
            response=response_body,
    )
    crud.create_conversation(db=db, conversation=conversation)

    return Response(content=str(response), media_type="application/xml")


@app.get("/upload_warehouse")
async def upload_warehouse():
    upload_app_data_to_bq(project_id=PROJECT_ID, dataset=DATASET_NAME, engine=ENGINE)
    return


@app.get("/download_restaurants")
async def download_restaurants(db: Session = Depends(get_db), prod_flag=PROD_FLAG):
    # ds = (datetime.datetime.today() - datetime.timedelta(2)).strftime("%Y-%m-%d")
    ds = '2024-04-01'
    download_restaurants_from_bq(db=db, ds=ds, project_id=PROJECT_ID, prod_flag=prod_flag)
    return

@app.get("/download_restaurant_features")
async def download_restaurant_features(db: Session = Depends(get_db)):
    download_features_from_bq(db=db, project_id=PROJECT_ID)
    return