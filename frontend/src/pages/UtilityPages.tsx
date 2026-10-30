import { useEffect, useState } from 'react';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import { BookCard } from '../components/BookCard';
import { StatePanel } from '../components/StatePanel';
import { useAuth } from '../context/AuthContext';
import { useWishlist } from '../hooks/useWishlist';
import type { Loan } from '../types';

export function WishlistPage() {
  const wishlist = useWishlist();
  if (wishlist.loading) return <StatePanel kind="loading" title="Открываем вашу полку" text="Загружаем сохранённые книги…" />;
  return <section className="page"><p className="eyebrow">Личная полка</p><h1>Хочу прочитать</h1>{wishlist.error ? <StatePanel kind="error" title="Не удалось загрузить список" text={wishlist.error} /> : wishlist.books.length ? <div className="book-grid">{wishlist.books.map(book => <BookCard key={book.id} book={book} onWishlist={item => void wishlist.toggle(item)} isSaved />)}</div> : <div className="empty-box"><h2>Список пока пуст</h2><p>Добавляйте книги сердечком в каталоге — они появятся здесь.</p><Link className="button" to="/books">Открыть каталог</Link></div>}</section>;
}

export function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    if (!user) { setLoading(false); return; }
    api<Loan[]>(user.role === 'librarian' ? '/loans' : '/loans/mine').then(setLoans).catch(reason => setError(reason instanceof Error ? reason.message : 'Не удалось загрузить выдачи')).finally(() => setLoading(false));
  }, [user]);
  if (authLoading) return <StatePanel kind="loading" title="Открываем кабинет" text="Проверяем профиль…" />;
  if (!user) return <Navigate to="/login" replace />;
  return <section className="page"><p className="eyebrow">Личный кабинет</p><h1>{user.profile?.full_name || user.email}</h1><div className="dashboard-grid"><article><h2>Роль</h2><p>{user.role === 'librarian' ? 'Библиотекарь' : 'Читатель'}</p><p>{user.email}</p></article><article><h2>Сохранённые книги</h2><p>Список синхронизируется с профилем после входа.</p><Link to="/wishlist">Открыть список</Link></article><article><h2>Быстрые действия</h2><Link to="/books">Выбрать книгу</Link></article></div><section className="loans-section"><div className="section-head"><div><p className="eyebrow">Учёт экземпляров</p><h2>{user.role === 'librarian' ? 'Все выдачи' : 'Мои выдачи'}</h2></div><span>{loans.filter(loan => !loan.returned_at).length} активных</span></div>{loading ? <StatePanel kind="loading" title="Загружаем выдачи" text="Проверяем журнал библиотеки…" /> : error ? <StatePanel kind="error" title="Не удалось загрузить выдачи" text={error} /> : loans.length ? <div className="loan-list">{loans.map(loan => <article key={loan.id} className="loan-row"><div><h3>{loan.book.title}</h3><p>{loan.book.author.name}</p></div><dl><div><dt>Вернуть до</dt><dd>{new Date(loan.due_date).toLocaleDateString('ru-RU')}</dd></div><div><dt>Статус</dt><dd>{loan.returned_at ? 'Возвращена' : 'На руках'}</dd></div></dl>{!loan.returned_at && <ReturnButton loanId={loan.id} onReturned={() => setLoans(current => current.map(item => item.id === loan.id ? {...item, returned_at: new Date().toISOString()} : item))} />}</article>)}</div> : <div className="empty-box"><h2>Выдач пока нет</h2><p>Выберите доступную книгу в каталоге.</p><Link className="button" to="/books">Перейти в каталог</Link></div>}</section></section>;
}

function ReturnButton({ loanId, onReturned }: { loanId: number; onReturned: () => void }) {
  const [busy, setBusy] = useState(false);
  const returnBook = async () => { setBusy(true); try { await api(`/loans/${loanId}/return`, { method: 'POST' }); onReturned(); } finally { setBusy(false); } };
  return <button className="button button--ghost" onClick={() => void returnBook()} disabled={busy}>{busy ? 'Возвращаем…' : 'Вернуть'}</button>;
}

export function LoanPage() {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const bookId = Number(params.get('book'));
  const minDate = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
  const [dueDate, setDueDate] = useState(minDate);
  if (!user) return <Navigate to="/login" replace />;
  const submit = async (event: React.FormEvent) => { event.preventDefault(); setMessage(''); try { await api('/loans', { method: 'POST', body: JSON.stringify({ book_id: bookId, due_date: dueDate }) }); navigate('/dashboard'); } catch (error) { setMessage(error instanceof Error ? error.message : 'Не удалось оформить выдачу'); } };
  return <section className="auth-card"><p className="eyebrow">Выдача книги</p><h1>Оформить выдачу</h1><form onSubmit={submit}><label className="field">Книга<input value={bookId || ''} readOnly /></label><label className="field">Срок возврата<input type="date" min={minDate} value={dueDate} onChange={event => setDueDate(event.target.value)} required /></label><label className="field">Количество дней<input type="number" min="1" max="30" defaultValue="14" required /></label><label className="field">E-mail<input type="email" value={user.email} readOnly /></label><label className="field">Комментарий<textarea maxLength={500} /></label><label className="check"><input type="checkbox" required /> Я принимаю правила библиотеки</label>{message && <p className="form-error" role="alert">{message}</p>}<button className="button" type="submit">Подтвердить выдачу</button></form></section>;
}

export function NotFound() {
  return <section className="page not-found"><span>404</span><h1>Эта полка ещё не собрана</h1><p>Страница не существует или была перемещена.</p><Link className="button" to="/books">Вернуться в каталог</Link></section>;
}
