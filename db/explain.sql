-- Выполнить до и после создания ix_books_title_lower.
EXPLAIN (ANALYZE, BUFFERS) SELECT id, title FROM books WHERE lower(title) LIKE 'книга 2%';
-- Выполнить до и после создания ix_loans_due_active.
EXPLAIN (ANALYZE, BUFFERS) SELECT id, user_id, book_id FROM loans WHERE returned_at IS NULL AND due_date < current_date;
