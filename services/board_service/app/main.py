from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlmodel import SQLModel, Field, select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, Annotated, List
from database import get_session, init_db

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

app = FastAPI(title="Board Service")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/api/board/posts", response_model=List[BoardPost])
async def list_posts(session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(select(BoardPost).order_by(BoardPost.id.desc()))
    return result.scalars().all()

@app.get("/api/board/posts/{post_id}", response_model=BoardPost)
async def get_post(post_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    post = await session.get(BoardPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/api/board/posts", response_model=BoardPost, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: BoardPostCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_user_id: Annotated[int, Header(alias="X-User-Id")],
):
    new_post = BoardPost(**post_data.dict(), owner_id=x_user_id)
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post

@app.patch("/api/board/posts/{post_id}", response_model=BoardPost)
async def update_post(
    post_id: int,
    post_data: BoardPostUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_user_id: Annotated[int, Header(alias="X-User-Id")],
):
    post = await session.get(BoardPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != x_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in post_data.dict(exclude_unset=True).items():
        setattr(post, field, value)
    await session.commit()
    await session.refresh(post)
    return post

@app.delete("/api/board/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_user_id: Annotated[int, Header(alias="X-User-Id")],
):
    post = await session.get(BoardPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != x_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await session.delete(post)
    await session.commit()
    return