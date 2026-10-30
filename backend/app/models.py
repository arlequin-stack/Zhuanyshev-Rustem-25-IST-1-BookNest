from datetime import date, datetime
from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

book_genres = Table(
    "book_genres", Base.metadata,
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

wishlist = Table(
    "wishlist", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    loans: Mapped[list["Loan"]] = relationship(back_populates="user")
    wished_books: Mapped[list["Book"]] = relationship(secondary=wishlist, back_populates="wishers")
    __table_args__ = (CheckConstraint("role IN ('member','librarian')", name="ck_user_role"),)

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(32))
    user: Mapped[User] = relationship(back_populates="profile")

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    bio: Mapped[str | None] = mapped_column(Text)
    books: Mapped[list["Book"]] = relationship(back_populates="author")

class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    books: Mapped[list["Book"]] = relationship(secondary=book_genres, back_populates="genres")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(240), index=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    year: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float, default=0)
    copies_total: Mapped[int] = mapped_column(Integer, default=1)
    copies_available: Mapped[int] = mapped_column(Integer, default=1)
    cover_url: Mapped[str | None] = mapped_column(String(500))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="RESTRICT"), index=True)
    author: Mapped[Author] = relationship(back_populates="books")
    genres: Mapped[list[Genre]] = relationship(secondary=book_genres, back_populates="books")
    loans: Mapped[list["Loan"]] = relationship(back_populates="book")
    wishers: Mapped[list[User]] = relationship(secondary=wishlist, back_populates="wished_books")
    __table_args__ = (
        CheckConstraint("year >= 1450", name="ck_book_year"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_book_rating"),
        CheckConstraint("copies_total >= 0", name="ck_book_total"),
        CheckConstraint("copies_available >= 0 AND copies_available <= copies_total", name="ck_book_available"),
    )

class Loan(Base):
    __tablename__ = "loans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="RESTRICT"), index=True)
    loaned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    due_date: Mapped[date] = mapped_column(Date)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="loans")
    book: Mapped[Book] = relationship(back_populates="loans")
    __table_args__ = (UniqueConstraint("user_id", "book_id", "returned_at", name="uq_active_loan"),)

