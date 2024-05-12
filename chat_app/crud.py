from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_restaurant(db: Session, restaurant_id: int):
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()

def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    db_restaurant = models.Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def create_place(db: Session, place: schemas.PlaceCreate):
    db_place = models.Place(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


def create_engagement(db: Session, engagement: schemas.EngagementCreate):
    db_engagment = models.Engagement(**engagement.dict())
    db.add(db_engagment)
    db.commit()
    db.refresh(db_engagment)
    return db_engagment


def create_conversation(db: Session, conversation: schemas.ConversationCreate):
    db_conversation = models.Conversation(**conversation.dict())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation
