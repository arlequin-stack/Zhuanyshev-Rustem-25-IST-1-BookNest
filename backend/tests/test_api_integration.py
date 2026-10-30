from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Author, Book, Genre, Loan, Profile, User
from app.security import create_access_token, hash_password


@pytest.fixture()
def api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)

    def override_db():
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        yield client, testing_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def add_user(session_factory, email: str, role: str = "member") -> User:
    with session_factory() as db:
        user = User(email=email, password_hash=hash_password("Password1"), role=role, profile=Profile(full_name="Test User"))
        db.add(user); db.commit(); db.refresh(user)
        return user


def add_catalog(session_factory, copies: int = 1) -> Book:
    with session_factory() as db:
        author = Author(name="Test Author")
        genre = Genre(name="Technology")
        book = Book(title="Test Book", isbn="9781234567890", description="A sufficiently long test description.", year=2026, rating=4.5, copies_total=copies, copies_available=copies, author=author, genres=[genre])
        db.add(book); db.commit(); db.refresh(book)
        return book


def auth(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


def test_register_returns_201(api):
    client, _ = api
    response = client.post("/api/v1/auth/register", json={"email":"new@example.com", "password":"Password1", "full_name":"New User"})
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


def test_login_and_refresh_return_token_pairs(api):
    client, sessions = api
    add_user(sessions, "member@example.com")
    login = client.post("/api/v1/auth/token", data={"username":"member@example.com", "password":"Password1"})
    assert login.status_code == 200
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token":login.json()["refresh_token"]})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


def test_catalog_write_without_token_returns_401(api):
    client, _ = api
    response = client.post("/api/v1/books", json={})
    assert response.status_code == 401


def test_member_cannot_create_book(api):
    client, sessions = api
    member = add_user(sessions, "member@example.com")
    response = client.post("/api/v1/books", headers=auth(member), json={})
    assert response.status_code == 403


def test_librarian_creates_book_and_duplicate_is_409(api):
    client, sessions = api
    librarian = add_user(sessions, "librarian@example.com", "librarian")
    with sessions() as db:
        author = Author(name="API Author"); genre = Genre(name="API Genre")
        db.add_all([author, genre]); db.commit(); author_id, genre_id = author.id, genre.id
    payload = {"title":"API Book", "isbn":"9781111111111", "description":"A valid description for the API book.", "year":2026, "copies_total":2, "author_id":author_id, "genre_ids":[genre_id]}
    created = client.post("/api/v1/books", headers=auth(librarian), json=payload)
    duplicate = client.post("/api/v1/books", headers=auth(librarian), json=payload)
    assert created.status_code == 201
    assert duplicate.status_code == 409


def test_missing_book_is_404(api):
    client, _ = api
    response = client.get("/api/v1/books/999")
    assert response.status_code == 404


def test_invalid_book_is_422(api):
    client, sessions = api
    librarian = add_user(sessions, "librarian@example.com", "librarian")
    response = client.post("/api/v1/books", headers=auth(librarian), json={"title":"x", "isbn":"bad"})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


def test_unavailable_book_is_409(api):
    client, sessions = api
    member = add_user(sessions, "member@example.com")
    book = add_catalog(sessions, copies=0)
    response = client.post("/api/v1/loans", headers=auth(member), json={"book_id":book.id, "due_date":str(date.today() + timedelta(days=7))})
    assert response.status_code == 409


def test_foreign_loan_is_hidden_with_404(api):
    client, sessions = api
    owner = add_user(sessions, "owner@example.com")
    stranger = add_user(sessions, "stranger@example.com")
    book = add_catalog(sessions)
    with sessions() as db:
        loan = Loan(user_id=owner.id, book_id=book.id, due_date=date.today() + timedelta(days=7))
        db.add(loan); db.commit(); db.refresh(loan); loan_id = loan.id
    response = client.get(f"/api/v1/loans/{loan_id}", headers=auth(stranger))
    assert response.status_code == 404
