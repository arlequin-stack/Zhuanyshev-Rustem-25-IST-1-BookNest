from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app import models, schemas
from app.deps import Db, Librarian

router = APIRouter(prefix="/authors", tags=["authors"])

def find(db: Db, author_id: int) -> models.Author:
    author = db.get(models.Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return author

@router.get("", response_model=list[schemas.AuthorRead])
def all_authors(db: Db):
    return list(db.scalars(select(models.Author).order_by(models.Author.name)).all())

@router.get("/{author_id}", response_model=schemas.AuthorRead)
def one_author(author_id: int, db: Db):
    return find(db, author_id)

@router.get("/{author_id}/books", response_model=list[schemas.BookRead])
def author_books(author_id: int, db: Db):
    find(db, author_id)
    return list(db.scalars(select(models.Book).options(selectinload(models.Book.author), selectinload(models.Book.genres)).where(models.Book.author_id == author_id)).all())

@router.post("", response_model=schemas.AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(data: schemas.AuthorCreate, db: Db, _: Librarian):
    if db.scalar(select(models.Author).where(models.Author.name == data.name)):
        raise HTTPException(status_code=409, detail="Автор уже существует")
    author = models.Author(**data.model_dump()); db.add(author); db.commit(); db.refresh(author)
    return author

@router.patch("/{author_id}", response_model=schemas.AuthorRead)
def update_author(author_id: int, data: schemas.AuthorUpdate, db: Db, _: Librarian):
    author = find(db, author_id)
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(author, key, value)
    db.commit(); db.refresh(author); return author

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Db, _: Librarian):
    db.delete(find(db, author_id)); db.commit(); return Response(status_code=204)

