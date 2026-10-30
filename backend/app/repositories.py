from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app import models


def get_book(db: Session, book_id: int, *, lock: bool = False) -> models.Book | None:
    statement = select(models.Book).options(selectinload(models.Book.author), selectinload(models.Book.genres)).where(models.Book.id == book_id)
    if lock:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_books(db: Session, q: str | None, genre: int | None, available_only: bool, page: int, size: int, sort: str) -> tuple[list[models.Book], int]:
    filters = []
    if q:
        filters.append(or_(models.Book.title.ilike(f"%{q}%"), models.Book.isbn.ilike(f"%{q}%"), models.Book.author.has(models.Author.name.ilike(f"%{q}%"))))
    if genre is not None:
        filters.append(models.Book.genres.any(models.Genre.id == genre))
    if available_only:
        filters.append(models.Book.copies_available > 0)
    order = {"title": models.Book.title.asc(), "year": models.Book.year.desc(), "rating": models.Book.rating.desc()}.get(sort, models.Book.title.asc())
    total = db.scalar(select(func.count(models.Book.id)).where(*filters)) or 0
    items = list(db.scalars(select(models.Book).options(selectinload(models.Book.author), selectinload(models.Book.genres)).where(*filters).order_by(order, models.Book.id).offset((page - 1) * size).limit(size)).all())
    return items, total


def isbn_exists(db: Session, isbn: str, exclude_id: int | None = None) -> bool:
    statement = select(models.Book.id).where(models.Book.isbn == isbn)
    if exclude_id is not None:
        statement = statement.where(models.Book.id != exclude_id)
    return db.scalar(statement) is not None


def genres_by_ids(db: Session, genre_ids: list[int]) -> list[models.Genre]:
    return list(db.scalars(select(models.Genre).where(models.Genre.id.in_(genre_ids))).all()) if genre_ids else []


def active_loan(db: Session, user_id: int, book_id: int) -> models.Loan | None:
    return db.scalar(select(models.Loan).where(models.Loan.user_id == user_id, models.Loan.book_id == book_id, models.Loan.returned_at.is_(None)))


def get_loan(db: Session, loan_id: int) -> models.Loan | None:
    return db.scalar(select(models.Loan).options(selectinload(models.Loan.book).selectinload(models.Book.author), selectinload(models.Loan.book).selectinload(models.Book.genres)).where(models.Loan.id == loan_id))
