from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models, repositories, schemas

def list_books(db: Session, q: str | None, genre: int | None, available_only: bool, page: int, size: int, sort: str) -> schemas.BookPage:
    items, total = repositories.list_books(db, q, genre, available_only, page, size, sort)
    return schemas.BookPage(items=items, total=total, page=page, size=size)

def create_book(db: Session, data: schemas.BookCreate) -> models.Book:
    if repositories.isbn_exists(db, data.isbn):
        raise HTTPException(status_code=409, detail="Книга с таким ISBN уже существует")
    genres = repositories.genres_by_ids(db, data.genre_ids)
    book = models.Book(**data.model_dump(exclude={"genre_ids"}), copies_available=data.copies_total, genres=genres)
    db.add(book); db.commit(); db.refresh(book)
    return book

def update_book(db: Session, book: models.Book, data: schemas.BookUpdate) -> models.Book:
    values = data.model_dump(exclude_unset=True)
    genre_ids = values.pop("genre_ids", None)
    if "isbn" in values and values["isbn"] != book.isbn:
        if repositories.isbn_exists(db, values["isbn"], book.id):
            raise HTTPException(status_code=409, detail="Книга с таким ISBN уже существует")
    if genre_ids is not None:
        book.genres = repositories.genres_by_ids(db, genre_ids)
    for key, value in values.items():
        setattr(book, key, value)
    if book.copies_available > book.copies_total:
        book.copies_available = book.copies_total
    db.commit(); db.refresh(book)
    return book

def issue_book(db: Session, user: models.User, data: schemas.LoanCreate) -> models.Loan:
    book = repositories.get_book(db, data.book_id, lock=True)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if book.copies_available < 1:
        raise HTTPException(status_code=409, detail="Нет свободных экземпляров")
    active = repositories.active_loan(db, user.id, book.id)
    if active:
        raise HTTPException(status_code=409, detail="Эта книга уже выдана пользователю")
    book.copies_available -= 1
    loan = models.Loan(user_id=user.id, book_id=book.id, due_date=data.due_date)
    db.add(loan); db.commit(); db.refresh(loan)
    return loan

def return_book(db: Session, loan: models.Loan) -> models.Loan:
    if loan.returned_at:
        raise HTTPException(status_code=409, detail="Книга уже возвращена")
    loan.returned_at = datetime.now(timezone.utc)
    loan.book.copies_available += 1
    db.commit(); db.refresh(loan)
    return loan

