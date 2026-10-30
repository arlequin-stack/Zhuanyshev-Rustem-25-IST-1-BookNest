from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app import models, schemas
from app.deps import CurrentUser, Db

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.get("", response_model=list[schemas.BookRead])
def get_wishlist(db: Db, user: CurrentUser):
    current = db.scalar(select(models.User).options(selectinload(models.User.wished_books).selectinload(models.Book.author), selectinload(models.User.wished_books).selectinload(models.Book.genres)).where(models.User.id == user.id))
    return current.wished_books if current else []

@router.post("/{book_id}", response_model=schemas.BookRead, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(book_id: int, db: Db, user: CurrentUser):
    book = db.scalar(select(models.Book).options(selectinload(models.Book.author), selectinload(models.Book.genres)).where(models.Book.id == book_id))
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    db.refresh(user, attribute_names=["wished_books"])
    if any(item.id == book_id for item in user.wished_books):
        raise HTTPException(status_code=409, detail="Книга уже в списке")
    user.wished_books.append(book)
    db.commit()
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(book_id: int, db: Db, user: CurrentUser):
    db.refresh(user, attribute_names=["wished_books"])
    book = next((item for item in user.wished_books if item.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Книга отсутствует в списке")
    user.wished_books.remove(book)
    db.commit()
    return Response(status_code=204)

