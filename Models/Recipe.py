from pydantic import BaseModel, Field, field_validator

from typing import Optional
from datetime import date
import base64

class Recipe(BaseModel):
    recipe_id: int
    recipe_name: str = Field(..., max_length=255)
    date_created: date
    recipe_image: bytes
    recipe_description: str = Field(..., max_length=3000)
    instructions: str = Field(..., max_length=3000)
    tags: list[str]
    user_id: int
