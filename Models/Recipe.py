from pydantic import BaseModel, Field, field_validator

from typing import Optional
from datetime import date
import base64

class Recipe(BaseModel):
    recipe_id: int
    recipe_name: str = Field(..., max_length=255)
    date_created: date
    recipe_image: Optional[str] # "Base64 encoded recipe image."
    recipe_description: str = Field(..., max_length=3000)
    instructions: str = Field(..., max_length=3000)
    tags: list[str]
    user_id: int

    @field_validator("recipe_image")
    def encode_recipe_image(cls, value):
        """Encodes the image in Base64 if it's provided as bytes."""
        if isinstance(value, bytes):
            return base64.b64encode(value).decode('utf-8')
        return value
