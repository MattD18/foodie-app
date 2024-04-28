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
    request: Request, From: str = Form(...), Body: str = Form(...) 
):
    
    #TODO: use proper validator
    # https://www.twilio.com/docs/usage/webhooks/webhooks-security
    is_twilio = request.headers.get("X-Twilio-Signature", False)
    if not is_twilio:
        raise HTTPException(status_code=400, detail="Error in Twilio Signature")
    
    response = MessagingResponse()
    msg = response.message(f"Hi {From}, you said: {Body}")
    return Response(content=str(response), media_type="application/xml")