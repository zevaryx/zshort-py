from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ShortURL(BaseModel):
    id: str
    long_url: str
    slug: str
    title: Optional[str] = None
    visits: int
    created_at: datetime
    edited_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    owner: str
    url: str
