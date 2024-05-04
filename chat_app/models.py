from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Float,
    Table, ForeignKey
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "smsbot_foodieuser"
    id = Column(Integer, primary_key=True)
    password = Column(String)
    last_login = Column(DateTime)
    is_superuser = Column(Boolean)
    phone_number = Column(String)
    is_staff = Column(Boolean)
    is_active = Column(Boolean)
    date_joined = Column(DateTime)
    created_at = Column(DateTime)

# Association Table for many-to-many relationship
association_table = Table(
    'smsbot_restaurant_place_tags', Base.metadata,
    Column('restaurant_id', Integer, ForeignKey('smsbot_restaurant.id')),
    Column('place_id', Integer, ForeignKey('smsbot_place.id'))
)

class Restaurant(Base):
    __tablename__ = "smsbot_restaurant"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    created_at = Column(DateTime)
    google_maps_url = Column(String)
    ranking_quality_score = Column(Float)
    # # # Establish many-to-many relationship with Place model
    places = relationship("Place", secondary=association_table, back_populates="restaurants")


class Place(Base):
    __tablename__ = "smsbot_place"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    geo = Column(String)

    # # Establish many-to-many relationship with Place model
    restaurants = relationship("Restaurant", secondary=association_table, back_populates="places")
    
class Engagement(Base):
    __tablename__ = "smsbot_engagement"
    id = Column(Integer, primary_key = True)
    action = Column(String)
    created_at = Column(DateTime)
    restaurant_id = Column(Integer, ForeignKey('smsbot_restaurant.id'))
    user_id = Column(Integer, ForeignKey('smsbot_foodieuser.id'))

class Conversation(Base):
    __tablename__ = "smsbot_conversation"
    id = Column(Integer, primary_key = True)
    ts = Column(String)
    sender = Column(String) 
    message = Column(String) 
    response = Column(String)   
