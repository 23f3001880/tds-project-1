# Pydantic Models Here
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import base64

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    image: Optional[str] = None

    @field_validator("image")
    def validate_base64_image(cls, v):
        if v is None:
            return v
        try:
            decoded = base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("Image must be a valid base64-encoded string.")
        
        if len(decoded) > MAX_IMAGE_SIZE_BYTES:
            raise ValueError(f"Decoded image size exceeds {MAX_IMAGE_SIZE_BYTES / (1024*1024)} MB limit.")
        
        return v
