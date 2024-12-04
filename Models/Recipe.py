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

    @field_validator("recipe_name", "recipe_description", "instructions", mode="before")
    def validate_length(cls, value: str, info:"ValidationInfo") -> str:
        """Ensures string fields do not exceed their maximum length."""
        field_name = info.field_name
        field_schema = info.field_schema
        max_length = field_schema.get("max_length")
        if max_length and len(value) > max_length:
            raise ValueError(f"{field_name} exceeds the maximum length of {max_length} characters.")
        return value

    @field_validator("tags", mode='before', check_fields=True)
    def validate_tags(cls, value):
        """Ensures tags are a list of strings."""
        if not isinstance(value, list) or not all(isinstance(tag, str) for tag in value):
            raise ValueError("Tags must be a list of strings.")
        return value
