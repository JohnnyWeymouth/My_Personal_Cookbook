from pydantic import BaseModel
from typing import Optional
from datetime import date

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
    recipe_image: Optional[bytes]
    recipe_description: str
    instructions: str
    tags: list[str]
    user_id: int

class PcbEntry(BaseModel):
    user_id: int
    recipe_id: int