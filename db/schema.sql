BEGIN;

CREATE TABLE authors (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(160) NOT NULL UNIQUE,
  bio TEXT
);
CREATE TABLE genres (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(80) NOT NULL UNIQUE
);
CREATE TABLE users (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'member' CHECK (role IN ('member','librarian')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE profiles (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  full_name VARCHAR(120) NOT NULL,
  phone VARCHAR(32)
);
CREATE TABLE books (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title VARCHAR(240) NOT NULL,
  isbn VARCHAR(20) NOT NULL UNIQUE,
  description TEXT NOT NULL CHECK (length(description) >= 20),
  year INTEGER NOT NULL CHECK (year BETWEEN 1450 AND 2100),
  rating NUMERIC(2,1) NOT NULL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
  copies_total INTEGER NOT NULL DEFAULT 1 CHECK (copies_total >= 0),
  copies_available INTEGER NOT NULL DEFAULT 1 CHECK (copies_available BETWEEN 0 AND copies_total),
  cover_url VARCHAR(500),
  author_id BIGINT NOT NULL REFERENCES authors(id) ON DELETE RESTRICT
);
CREATE TABLE book_genres (
  book_id BIGINT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  genre_id BIGINT NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
  PRIMARY KEY (book_id, genre_id)
);
CREATE TABLE loans (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  book_id BIGINT NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
  loaned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  due_date DATE NOT NULL,
  returned_at TIMESTAMPTZ,
  CHECK (due_date >= loaned_at::date),
  CHECK (returned_at IS NULL OR returned_at >= loaned_at)
);
CREATE UNIQUE INDEX uq_active_loan ON loans(user_id, book_id) WHERE returned_at IS NULL;
CREATE TABLE wishlist (
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  book_id BIGINT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, book_id)
);

CREATE INDEX ix_books_author_id ON books(author_id);
CREATE INDEX ix_books_title_lower ON books(lower(title));
CREATE INDEX ix_loans_due_active ON loans(due_date) WHERE returned_at IS NULL;
CREATE INDEX ix_loans_user_id ON loans(user_id);

COMMIT;
