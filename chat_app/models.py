from sqlalchemy import Boolean, Column, DateTime, Integer, String, Float
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

class Restaurant(Base):
    __tablename__ = "smsbot_restaurant"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    created_at = Column(DateTime)
    google_maps_url = Column(String)
    ranking_quality_score = Column(Float)