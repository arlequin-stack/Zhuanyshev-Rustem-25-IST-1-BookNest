BEGIN;

INSERT INTO authors(name) SELECT 'Автор ' || value FROM generate_series(1, 5) value;
INSERT INTO genres(name) VALUES ('Роман'), ('Наука'), ('Технологии'), ('История'), ('Саморазвитие');

INSERT INTO users(email, password_hash, role)
SELECT 'reader' || value || '@example.com', '$2b$12$3coPcHzt2SV0Q6f.IYGLZ.gG48p4BKttrPpF96c58GkgdA.BMGBXy',
       CASE WHEN value = 1 THEN 'librarian' ELSE 'member' END
FROM generate_series(1, 10) value;
INSERT INTO profiles(user_id, full_name)
SELECT id, 'Читатель ' || id FROM users;

INSERT INTO books(title, isbn, description, year, rating, copies_total, copies_available, author_id)
SELECT 'Книга ' || value,
       '9780000' || lpad(value::text, 6, '0'),
       'Демонстрационное описание книги для проверки каталога и SQL-запросов.',
       1990 + value,
       3 + (value % 20) / 10.0,
       3,
       3,
       ((value - 1) % 5) + 1
FROM generate_series(1, 30) value;
INSERT INTO book_genres(book_id, genre_id)
SELECT id, ((id - 1) % 5) + 1 FROM books;

INSERT INTO loans(user_id, book_id, loaned_at, due_date, returned_at)
SELECT ((value - 1) % 10) + 1,
       value,
       now() - (value || ' days')::interval,
       current_date + CASE WHEN value <= 5 THEN -value ELSE value END,
       CASE WHEN value BETWEEN 6 AND 10 THEN now() - interval '1 day' ELSE NULL END
FROM generate_series(1, 20) value;
UPDATE books SET copies_available = copies_available - 1
WHERE id IN (SELECT book_id FROM loans WHERE returned_at IS NULL);
INSERT INTO wishlist(user_id, book_id)
SELECT ((value - 1) % 10) + 1, value FROM generate_series(1, 15) value;

COMMIT;
