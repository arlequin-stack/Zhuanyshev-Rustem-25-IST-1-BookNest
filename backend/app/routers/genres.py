from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from app import models, schemas
from app.deps import Db, Librarian

router = APIRouter(prefix="/genres", tags=["genres"])

def get_genre_or_404(db: Db, genre_id: int) -> models.Genre:
    genre = db.get(models.Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    return genre

@router.get("", response_model=list[schemas.GenreRead])
def list_genres(db: Db):
    return list(db.scalars(select(models.Genre).order_by(models.Genre.name)).all())

@router.get("/{genre_id}", response_model=schemas.GenreRead)
def get_genre(genre_id: int, db: Db):
    return get_genre_or_404(db, genre_id)

@router.post("", response_model=schemas.GenreRead, status_code=status.HTTP_201_CREATED)
def create_genre(data: schemas.GenreCreate, db: Db, _: Librarian):
    if db.scalar(select(models.Genre).where(models.Genre.name == data.name)):
        raise HTTPException(status_code=409, detail="Жанр уже существует")
    genre = models.Genre(name=data.name)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre

@router.patch("/{genre_id}", response_model=schemas.GenreRead)
def update_genre(genre_id: int, data: schemas.GenreUpdate, db: Db, _: Librarian):
    genre = get_genre_or_404(db, genre_id)
    duplicate = db.scalar(select(models.Genre).where(models.Genre.name == data.name, models.Genre.id != genre_id))
    if duplicate:
        raise HTTPException(status_code=409, detail="Жанр уже существует")
    genre.name = data.name
    db.commit()
    db.refresh(genre)
    return genre

@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(genre_id: int, db: Db, _: Librarian):
    genre = get_genre_or_404(db, genre_id)
    if genre.books:
        raise HTTPException(status_code=409, detail="Нельзя удалить жанр, связанный с книгами")
    db.delete(genre)
    db.commit()
    return Response(status_code=204)

