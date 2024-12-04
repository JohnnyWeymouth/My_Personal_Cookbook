import base64
from datetime import date
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_id: int
    recipe_name: str
    date_created: date
    recipe_image: 
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

    @field_validator("recipe_image", pre=True, always=True)
    def encode_recipe_image(cls, value):
        """
        Encodes the image in Base64 if it's provided as bytes.
        """
        if isinstance(value, bytes):
            return base64.b64encode(value).decode('utf-8')
        return value

    @field_validator("recipe_name", "recipe_description", "instructions")
    def validate_length(cls, value, field):
        """
        Ensures string fields do not exceed their maximum length.
        """
        max_length = field.field_info.extra.get("max_length")
        if max_length and len(value) > max_length:
            raise ValueError(f"{field.name} exceeds maximum length of {max_length} characters.")
        return value

    @field_validator("tags", pre=True)
    def validate_tags(cls, value):
        """
        Ensures tags are a list of strings.
        """
        if not isinstance(value, list) or not all(isinstance(tag, str) for tag in value):
            raise ValueError("Tags must be a list of strings.")
        return value
