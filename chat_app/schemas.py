from typing import List, Union
from datetime import datetime


from pydantic import BaseModel

class RestaurantBase(BaseModel):
    id : int
    name: Union[str, None] = None
    address: Union[str, None] = None
    created_at: Union[datetime, None] = None
    google_maps_url: Union[str, None] = None
    ranking_quality_score: Union[float, None] = None

class UserBase(BaseModel):
    id : int
    password: Union[str, None] = None
    last_login: Union[datetime, None] = None
    is_superuser: Union[bool, None] = None
    phone_number: Union[str, None] = None
    is_staff: Union[bool, None] = None
    is_active: Union[bool, None] = None
    date_joined: Union[datetime, None] = None
    created_at: Union[datetime, None] = None

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    pass

class User(UserBase):

    class Config:
        from_attributes = True

