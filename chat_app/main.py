from typing import List

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

from . import crud, models, schemas, utils
from .database import SessionLocal, engine

from .query_parser import QueryParser
from .rec_engine import RecEngine

from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator  

env_vars = utils.get_env_vars()

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

    # classify query intent
    qp = QueryParser(db=db)
    user_intent = qp.classify_intent(user_query)

     # # process user query
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
    elif user_intent == 'FALLBACK':
        response_body = 'Text "Rec me <neighborhood>" for a local NYC food recommendation, for example: "Rec me Williamsburg"'
    else:
        response_body = 'Text "Rec me <neighborhood>" for a local NYC food recommendation, for example: "Rec me Williamsburg"'


    response = MessagingResponse()
    msg = response.message(response_body)

    #TODO log interaction in db
    return Response(content=str(response), media_type="application/xml")