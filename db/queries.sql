-- 1. Каталог с автором и агрегированными жанрами.
SELECT b.id, b.title, a.name AS author, string_agg(g.name, ', ' ORDER BY g.name) AS genres
FROM books b JOIN authors a ON a.id=b.author_id
LEFT JOIN book_genres bg ON bg.book_id=b.id LEFT JOIN genres g ON g.id=bg.genre_id
GROUP BY b.id, a.name ORDER BY b.title;

-- 2. Активные просроченные выдачи.
SELECT l.id, u.email, b.title, l.due_date, current_date-l.due_date AS overdue_days
FROM loans l JOIN users u ON u.id=l.user_id JOIN books b ON b.id=l.book_id
WHERE l.returned_at IS NULL AND l.due_date < current_date ORDER BY l.due_date;

-- 3. Топ авторов по числу выдач.
SELECT a.name, count(l.id) AS loan_count FROM authors a JOIN books b ON b.author_id=a.id
LEFT JOIN loans l ON l.book_id=b.id GROUP BY a.id ORDER BY loan_count DESC LIMIT 5;

-- 4. Читатели без единой выдачи.
SELECT u.id, u.email FROM users u LEFT JOIN loans l ON l.user_id=u.id
WHERE u.role='member' GROUP BY u.id HAVING count(l.id)=0;

-- 5. Статистика по жанрам.
SELECT g.name, count(DISTINCT b.id) AS books, count(l.id) AS loans
FROM genres g LEFT JOIN book_genres bg ON bg.genre_id=g.id LEFT JOIN books b ON b.id=bg.book_id
LEFT JOIN loans l ON l.book_id=b.id GROUP BY g.id ORDER BY loans DESC;

-- 6. Стабильная пагинация каталога.
SELECT id, title FROM books ORDER BY title, id LIMIT 10 OFFSET 10;

-- 7. Поиск по названию без учёта регистра.
SELECT id, title FROM books WHERE lower(title) LIKE lower('%книга 2%') ORDER BY title;

-- 8. Доступность экземпляров, вычисленная по активным выдачам.
SELECT b.id, b.title, b.copies_total-count(l.id) AS calculated_available
FROM books b LEFT JOIN loans l ON l.book_id=b.id AND l.returned_at IS NULL GROUP BY b.id;

-- 9. История конкретного читателя.
SELECT b.title, l.loaned_at, l.due_date, l.returned_at FROM loans l
JOIN books b ON b.id=l.book_id WHERE l.user_id=2 ORDER BY l.loaned_at DESC;

-- 10. Самые желаемые книги.
SELECT b.title, count(w.user_id) AS wishes FROM books b LEFT JOIN wishlist w ON w.book_id=b.id
GROUP BY b.id ORDER BY wishes DESC, b.title LIMIT 10;

-- 11. Средний рейтинг и число книг по автору.
SELECT a.name, count(b.id) AS books, round(avg(b.rating),2) AS avg_rating
FROM authors a LEFT JOIN books b ON b.author_id=a.id GROUP BY a.id ORDER BY avg_rating DESC NULLS LAST;

-- 12. Доля возвращённых вовремя книг.
SELECT round(100.0*count(*) FILTER (WHERE returned_at::date<=due_date)/NULLIF(count(*) FILTER (WHERE returned_at IS NOT NULL),0),2) AS returned_on_time_percent
FROM loans;
