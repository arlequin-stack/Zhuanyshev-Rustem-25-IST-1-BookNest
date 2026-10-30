import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Navigate, useNavigate, useParams } from 'react-router-dom';
import { z } from 'zod';
import { api } from '../api/client';
import { StatePanel } from '../components/StatePanel';
import { useAuth } from '../context/AuthContext';
import type { Author, Book, Genre } from '../types';

const schema = z.object({
  title: z.string().min(2, 'Минимум 2 символа'),
  isbn: z.string().regex(/^[0-9Xx-]{10,17}$/, 'Проверьте ISBN'),
  description: z.string().min(20, 'Минимум 20 символов'),
  year: z.coerce.number().min(1450).max(2100),
  rating: z.coerce.number().min(0).max(5),
  copies_total: z.coerce.number().min(0).max(10000),
  author_id: z.coerce.number().positive('Выберите автора'),
  genre_id: z.coerce.number().positive('Выберите жанр'),
});
type ValuesInput = z.input<typeof schema>;
type Values = z.output<typeof schema>;

export function BookFormPage() {
  const {user, loading: authLoading} = useAuth();
  const {id} = useParams();
  const navigate = useNavigate();
  const editing = Boolean(id);
  const [authors, setAuthors] = useState<Author[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [loading, setLoading] = useState(editing);
  const {register, handleSubmit, reset, setError, formState:{errors, isSubmitting}} = useForm<ValuesInput, unknown, Values>({resolver:zodResolver(schema), defaultValues:{rating:0, copies_total:1}});

  useEffect(() => {
    Promise.all([api<Author[]>('/authors'), api<Genre[]>('/genres'), editing ? api<Book>(`/books/${id}`) : Promise.resolve(null)])
      .then(([authorList, genreList, book]) => {
        setAuthors(authorList); setGenres(genreList);
        if (book) reset({...book, rating:Number(book.rating.toFixed(1)), genre_id:book.genres[0]?.id || 0});
      })
      .catch(error => setError('root', {message:error instanceof Error ? error.message : 'Не удалось загрузить форму'}))
      .finally(() => setLoading(false));
  }, [editing, id, reset, setError]);

  if (authLoading) return <StatePanel kind="loading" title="Проверяем доступ" text="Один момент…" />;
  if (!user) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  if (user.role !== 'librarian') return <Navigate to="/dashboard" replace />;
  if (loading) return <StatePanel kind="loading" title="Загружаем книгу" text="Один момент…" />;

  const submit = async (values: Values) => {
    try {
      const payload = {...values, genre_ids:[values.genre_id]};
      const book = await api<Book>(editing ? `/books/${id}` : '/books', {method:editing ? 'PATCH' : 'POST', body:JSON.stringify(payload)});
      navigate(`/books/${book.id}`);
    } catch (error) { setError('root', {message:error instanceof Error ? error.message : 'Не удалось сохранить книгу'}); }
  };

  return <section className="page"><p className="eyebrow">Панель библиотекаря</p><h1>{editing ? 'Редактировать книгу' : 'Добавить книгу'}</h1><form className="admin-form book-editor" onSubmit={handleSubmit(submit)} noValidate>
    <Field label="Название" error={errors.title?.message}><input aria-invalid={Boolean(errors.title)} {...register('title')} /></Field>
    <Field label="ISBN" error={errors.isbn?.message}><input aria-invalid={Boolean(errors.isbn)} {...register('isbn')} /></Field>
    <Field label="Описание" error={errors.description?.message}><textarea rows={6} aria-invalid={Boolean(errors.description)} {...register('description')} /></Field>
    <div className="field-pair"><Field label="Год" error={errors.year?.message}><input type="number" {...register('year')} /></Field><Field label="Рейтинг" error={errors.rating?.message}><input type="number" step="0.1" {...register('rating')} /></Field></div>
    <Field label="Количество экземпляров" error={errors.copies_total?.message}><input type="number" {...register('copies_total')} /></Field>
    <Field label="Автор" error={errors.author_id?.message}><select {...register('author_id')}><option value="">Выберите автора</option>{authors.map(author => <option key={author.id} value={author.id}>{author.name}</option>)}</select></Field>
    <Field label="Жанр" error={errors.genre_id?.message}><select {...register('genre_id')}><option value="">Выберите жанр</option>{genres.map(genre => <option key={genre.id} value={genre.id}>{genre.name}</option>)}</select></Field>
    {errors.root && <p className="form-error" role="alert">{errors.root.message}</p>}
    <div className="card-actions"><button className="button" disabled={isSubmitting}>{isSubmitting ? 'Сохраняем…' : 'Сохранить'}</button><button className="button button--ghost" type="button" onClick={() => navigate(-1)}>Отмена</button></div>
  </form></section>;
}

function Field({label, error, children}:{label:string; error?:string; children:React.ReactElement}) {
  return <label className="field">{label}{children}{error && <span className="form-error" role="alert">{error}</span>}</label>;
}
