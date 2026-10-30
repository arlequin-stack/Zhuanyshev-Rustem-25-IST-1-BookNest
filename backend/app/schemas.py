from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict | list | None = None
    request_id: str | None = None

class ProfileRead(BaseModel):
    full_name: str
    phone: str | None = None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=120)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("Пароль должен содержать буквы и цифры")
        return value

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: Literal["member", "librarian"]
    profile: ProfileRead | None = None
    model_config = ConfigDict(from_attributes=True)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class AuthorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    bio: str | None = Field(default=None, max_length=3000)

class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    bio: str | None = Field(default=None, max_length=3000)

class AuthorRead(AuthorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class GenreRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class GenreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)

class GenreUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=80)

class BookBase(BaseModel):
    title: str = Field(min_length=2, max_length=240)
    isbn: str = Field(pattern=r"^[0-9Xx-]{10,17}$")
    description: str = Field(min_length=20, max_length=5000)
    year: int = Field(ge=1450, le=2100)
    rating: float = Field(default=0, ge=0, le=5)
    copies_total: int = Field(default=1, ge=0, le=10000)
    cover_url: str | None = None
    author_id: int

class BookCreate(BookBase):
    genre_ids: list[int] = Field(default_factory=list, max_length=10)

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=240)
    isbn: str | None = Field(default=None, pattern=r"^[0-9Xx-]{10,17}$")
    description: str | None = Field(default=None, min_length=20, max_length=5000)
    year: int | None = Field(default=None, ge=1450, le=2100)
    rating: float | None = Field(default=None, ge=0, le=5)
    copies_total: int | None = Field(default=None, ge=0, le=10000)
    cover_url: str | None = None
    author_id: int | None = None
    genre_ids: list[int] | None = Field(default=None, max_length=10)

class BookRead(BookBase):
    id: int
    copies_available: int
    author: AuthorRead
    genres: list[GenreRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class BookPage(BaseModel):
    items: list[BookRead]
    total: int
    page: int
    size: int

class LoanCreate(BaseModel):
    book_id: int
    due_date: date

    @model_validator(mode="after")
    def due_date_must_be_future(self):
        if self.due_date <= date.today():
            raise ValueError("Дата возврата должна быть в будущем")
        return self

class LoanRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    loaned_at: datetime
    due_date: date
    returned_at: datetime | None
    book: BookRead
    model_config = ConfigDict(from_attributes=True)

