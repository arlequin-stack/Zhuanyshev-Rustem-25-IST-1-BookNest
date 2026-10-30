import pytest
from fastapi.testclient import TestClient
from jose import JWTError
from pydantic import ValidationError
from app.main import app
from app.schemas import BookCreate, LoanCreate, UserCreate
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

client = TestClient(app)

def test_register_rejects_weak_password_before_database():
    response = client.post('/api/v1/auth/register', json={'email':'user@example.com','password':'password','full_name':'Test User'})
    assert response.status_code == 422

def test_user_schema_accepts_strong_password():
    data = UserCreate(email='user@example.com', password='Password1', full_name='Test User')
    assert data.email == 'user@example.com'

def test_book_schema_rejects_old_year():
    with pytest.raises(ValidationError):
        BookCreate(title='Old', isbn='9781234567890', description='A sufficiently long description', year=1200, author_id=1)

def test_book_schema_rejects_bad_isbn():
    with pytest.raises(ValidationError):
        BookCreate(title='Book', isbn='abc', description='A sufficiently long description', year=2024, author_id=1)

def test_loan_requires_future_date():
    from datetime import date
    with pytest.raises(ValidationError):
        LoanCreate(book_id=1, due_date=date.today())

def test_password_hash_roundtrip():
    hashed = hash_password('Password123')
    assert hashed != 'Password123'
    assert verify_password('Password123', hashed)

def test_access_token_roundtrip():
    token = create_access_token(42, 'member')
    payload = decode_access_token(token)
    assert payload['sub'] == '42' and payload['role'] == 'member'

def test_refresh_token_roundtrip():
    token = create_refresh_token(42, 'librarian')
    payload = decode_refresh_token(token)
    assert payload['sub'] == '42' and payload['role'] == 'librarian'

def test_access_token_cannot_be_used_as_refresh_token():
    with pytest.raises(JWTError):
        decode_refresh_token(create_access_token(42, 'member'))

def test_invalid_token_rejected():
    with pytest.raises(JWTError):
        decode_access_token('not-a-token')

def test_docs_are_exposed():
    assert client.get('/api/docs').status_code == 200

def test_validation_error_has_unified_shape():
    response = client.post('/api/v1/auth/register', json={})
    body = response.json()
    assert response.status_code == 422
    assert body['code'] == 'validation_error'
    assert isinstance(body['details'], list)
    assert body['request_id']

def test_openapi_contains_wishlist_genres_and_refresh():
    paths = client.get('/api/openapi.json').json()['paths']
    assert '/api/v1/wishlist' in paths
    assert '/api/v1/genres' in paths
    assert '/api/v1/auth/refresh' in paths

