from pydantic import BaseModel
from typing import Optional

class UpdateProfile(BaseModel):
    nickname: Optional[str] = None
    name: Optional[str] = None