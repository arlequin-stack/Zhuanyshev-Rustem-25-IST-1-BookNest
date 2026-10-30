from fastapi import APIRouter, HTTPException, Query, Response, status
from app import models, repositories, schemas, services
from app.deps import Db, Librarian

router = APIRouter(prefix="/books", tags=["books"])

def get_book_or_404(db: Db, book_id: int) -> models.Book:
    book = repositories.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book

@router.get("", response_model=schemas.BookPage)
def list_books(db: Db, q: str | None = None, genre: int | None = None, available_only: bool = False, page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=50), sort: str = Query("title", pattern="^(title|year|rating)$")):
    return services.list_books(db, q, genre, available_only, page, size, sort)

@router.get("/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, db: Db):
    return get_book_or_404(db, book_id)

@router.post("", response_model=schemas.BookRead, status_code=status.HTTP_201_CREATED)
def create_book(data: schemas.BookCreate, db: Db, _: Librarian):
    return services.create_book(db, data)

@router.patch("/{book_id}", response_model=schemas.BookRead)
def update_book(book_id: int, data: schemas.BookUpdate, db: Db, _: Librarian):
    book = get_book_or_404(db, book_id)
    return services.update_book(db, book, data)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Db, _: Librarian):
    book = get_book_or_404(db, book_id)
    db.delete(book); db.commit()
    return Response(status_code=204)

