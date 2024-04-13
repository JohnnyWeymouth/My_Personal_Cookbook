from pydantic import BaseModel
from typing import Optional, Any
from datetime import date
import base64

class User(BaseModel):
    user_id: int
    username: str
    user_email: str
    first_name: str
    last_name: str
    password_hash: str
    date_joined: date

class Recipe(BaseModel):
    recipe_id: int
    recipe_name: str
    date_created: date
    recipe_image: Optional[Any]
    recipe_description: str
    instructions: str
    tags: list[str]
    user_id: int
    def __init__(self, **data):
        if 'recipe_image' in data and isinstance(data['recipe_image'], bytes):
            data['recipe_image'] = base64.b64encode(data['recipe_image']).decode('utf-8')
        else:
            data['recipe_image'] = None
        super().__init__(**data)

class PcbEntry(BaseModel):
    user_id: int
    recipe_id: int

class TryEntry(BaseModel):
    user_id: int
    recipe_id: int