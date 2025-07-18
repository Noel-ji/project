from typing import Optional
from sqlmodel import SQLModel, Field

class BoardPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    owner_id: int
    tags: Optional[str] = None

class BoardPostCreate(SQLModel):
    title: str
    content: str
    tags: Optional[str] = None

class BoardPostUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None