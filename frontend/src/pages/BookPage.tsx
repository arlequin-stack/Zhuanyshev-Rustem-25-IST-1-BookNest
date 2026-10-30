import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client';
import { StatePanel } from '../components/StatePanel';
import { useAuth } from '../context/AuthContext';
import type { Book } from '../types';

export function BookPage() {
  const {id} = useParams();
  const {user} = useAuth();
  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { api<Book>(`/books/${id}`).then(setBook).catch(reason => setError(reason.message)); }, [id]);
  if (error) return <StatePanel kind="error" title="Книга не найдена" text={error} />;
  if (!book) return <StatePanel kind="loading" title="Открываем карточку" text="Один момент…" />;
  return <article className="detail">
    <nav className="breadcrumbs" aria-label="Хлебные крошки"><Link to="/books">Каталог</Link><span>/</span><span>{book.title}</span></nav>
    <div className="detail-grid"><figure><div className="book-cover book-cover--large" aria-hidden="true"><span>{book.title.slice(0,2).toUpperCase()}</span></div><figcaption>{book.title}, {book.year}</figcaption></figure><section>
      <p className="eyebrow">{book.genres.map(genre => genre.name).join(' · ')}</p><h1>{book.title}</h1><p className="lead">{book.author.name}</p><p>{book.description}</p>
      <dl className="specs"><div><dt>ISBN</dt><dd>{book.isbn}</dd></div><div><dt>Год</dt><dd>{book.year}</dd></div><div><dt>Рейтинг</dt><dd>{book.rating}/5</dd></div><div><dt>Экземпляров</dt><dd>{book.copies_available} из {book.copies_total}</dd></div></dl>
      <div className="card-actions"><Link className="button" to={`/loans/new?book=${book.id}`}>{book.copies_available ? 'Взять книгу' : 'Сообщить о появлении'}</Link>{user?.role === 'librarian' && <Link className="button button--ghost" to={`/books/${book.id}/edit`}>Редактировать</Link>}</div>
    </section></div>
  </article>;
}
