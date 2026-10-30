import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Navigate } from 'react-router-dom';
import { z } from 'zod';
import { api } from '../api/client';
import { StatePanel } from '../components/StatePanel';
import { useAuth } from '../context/AuthContext';
import type { Author, Book, BookPage, Genre } from '../types';

const bookSchema = z.object({
  title: z.string().min(2, 'Введите название'),
  isbn: z.string().regex(/^[0-9Xx-]{10,17}$/, 'Проверьте ISBN'),
  description: z.string().min(20, 'Минимум 20 символов'),
  year: z.coerce.number().min(1450).max(2100),
  copies_total: z.coerce.number().min(1).max(10000),
  author_id: z.coerce.number().positive(),
  genre_id: z.coerce.number().positive(),
});
type BookFormInput = z.input<typeof bookSchema>;
type BookForm = z.output<typeof bookSchema>;

export function AdminPage() {
  const { user, loading: authLoading } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [authors, setAuthors] = useState<Author[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [authorName, setAuthorName] = useState('');
  const [genreName, setGenreName] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<BookFormInput, unknown, BookForm>({resolver:zodResolver(bookSchema)});

  const load = async () => {
    setLoading(true);
    try {
      const [bookPage, authorList, genreList] = await Promise.all([api<BookPage>('/books?size=50'), api<Author[]>('/authors'), api<Genre[]>('/genres')]);
      setBooks(bookPage.items); setAuthors(authorList); setGenres(genreList);
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Не удалось загрузить справочники'); }
    finally { setLoading(false); }
  };
  useEffect(() => { if (user?.role === 'librarian') void load(); }, [user]);
  if (authLoading) return <StatePanel kind="loading" title="Проверяем доступ" text="Один момент…" />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'librarian') return <Navigate to="/dashboard" replace />;

  const createBook = async (values: BookForm) => {
    setMessage('');
    try {
      await api('/books', {method:'POST', body:JSON.stringify({...values, rating:0, genre_ids:[values.genre_id]})});
      reset(); setMessage('Книга добавлена'); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Не удалось добавить книгу'); }
  };
  const createAuthor = async () => {
    if (authorName.trim().length < 2) return;
    try {
      await api('/authors', {method:'POST',body:JSON.stringify({name:authorName.trim()})});
      setAuthorName(''); setMessage('Автор добавлен'); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Не удалось добавить автора'); }
  };
  const createGenre = async () => {
    if (genreName.trim().length < 2) return;
    try {
      await api('/genres', {method:'POST',body:JSON.stringify({name:genreName.trim()})});
      setGenreName(''); setMessage('Жанр добавлен'); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Не удалось добавить жанр'); }
  };
  const remove = async (kind:'books'|'authors'|'genres', id:number, label:string) => {
    if (!window.confirm(`Удалить «${label}»? Это действие нельзя отменить.`)) return;
    try {
      await api(`/${kind}/${id}`, {method:'DELETE'}); setMessage('Запись удалена'); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Не удалось удалить запись'); }
  };

  return <section className="page admin-page"><p className="eyebrow">Панель библиотекаря</p><h1>Управление каталогом</h1>{message && <p className="notice" role="status">{message}</p>}<div className="admin-layout"><form className="admin-form" onSubmit={handleSubmit(createBook)}><h2>Новая книга</h2><label className="field">Название<input {...register('title')} />{errors.title && <span className="form-error">{errors.title.message}</span>}</label><label className="field">ISBN<input {...register('isbn')} />{errors.isbn && <span className="form-error">{errors.isbn.message}</span>}</label><label className="field">Описание<textarea rows={5} {...register('description')} />{errors.description && <span className="form-error">{errors.description.message}</span>}</label><div className="field-pair"><label className="field">Год<input type="number" {...register('year')} />{errors.year && <span className="form-error">{errors.year.message}</span>}</label><label className="field">Экземпляры<input type="number" {...register('copies_total')} />{errors.copies_total && <span className="form-error">{errors.copies_total.message}</span>}</label></div><label className="field">Автор<select {...register('author_id')}><option value="">Выберите автора</option>{authors.map(author=><option key={author.id} value={author.id}>{author.name}</option>)}</select>{errors.author_id && <span className="form-error">Выберите автора</span>}</label><label className="field">Жанр<select {...register('genre_id')}><option value="">Выберите жанр</option>{genres.map(genre=><option key={genre.id} value={genre.id}>{genre.name}</option>)}</select>{errors.genre_id && <span className="form-error">Выберите жанр</span>}</label><button className="button" disabled={isSubmitting}>{isSubmitting?'Добавляем…':'Добавить книгу'}</button></form><div className="admin-side"><QuickCreate title="Новый автор" value={authorName} onChange={setAuthorName} onSubmit={()=>void createAuthor()} /><QuickCreate title="Новый жанр" value={genreName} onChange={setGenreName} onSubmit={()=>void createGenre()} /><p>Книг: <strong>{books.length}</strong> · Авторов: <strong>{authors.length}</strong> · Жанров: <strong>{genres.length}</strong></p></div></div>{loading ? <StatePanel kind="loading" title="Обновляем каталог" text="Загружаем записи…" /> : <div className="admin-tables"><AdminList title="Книги" items={books.map(book=>({id:book.id,label:book.title,meta:book.author.name}))} onDelete={(id,label)=>void remove('books',id,label)} /><AdminList title="Авторы" items={authors.map(author=>({id:author.id,label:author.name}))} onDelete={(id,label)=>void remove('authors',id,label)} /><AdminList title="Жанры" items={genres.map(genre=>({id:genre.id,label:genre.name}))} onDelete={(id,label)=>void remove('genres',id,label)} /></div>}</section>;
}

function QuickCreate({title,value,onChange,onSubmit}:{title:string;value:string;onChange:(value:string)=>void;onSubmit:()=>void}) {
  return <form className="quick-create" onSubmit={event=>{event.preventDefault();onSubmit()}}><label className="field">{title}<input value={value} onChange={event=>onChange(event.target.value)} required minLength={2} /></label><button className="button button--ghost">Добавить</button></form>;
}

function AdminList({title,items,onDelete}:{title:string;items:{id:number;label:string;meta?:string}[];onDelete:(id:number,label:string)=>void}) {
  return <section className="admin-list"><h2>{title}</h2>{items.map(item=><article key={item.id}><div><strong>{item.label}</strong>{item.meta&&<small>{item.meta}</small>}</div><button className="danger-button" onClick={()=>onDelete(item.id,item.label)} aria-label={`Удалить ${item.label}`}>Удалить</button></article>)}</section>;
}
