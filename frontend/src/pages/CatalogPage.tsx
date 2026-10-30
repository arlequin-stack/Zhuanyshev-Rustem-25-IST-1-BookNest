import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import { BookCard } from '../components/BookCard';
import { StatePanel } from '../components/StatePanel';
import { useBooks } from '../hooks/useBooks';
import { useDebounce } from '../hooks/useDebounce';
import { useWishlist } from '../hooks/useWishlist';
import type { Genre } from '../types';

export function CatalogPage() {
  const [params, setParams] = useSearchParams({page: '1', sort: 'title'});
  const [genres, setGenres] = useState<Genre[]>([]);
  const debouncedSearch = useDebounce(params.get('q') || '', 350);
  const query = useMemo(() => {
    const next = new URLSearchParams(params);
    if (debouncedSearch) next.set('q', debouncedSearch); else next.delete('q');
    return next.toString();
  }, [debouncedSearch, params]);
  const {data, loading, error} = useBooks(query);
  const wishlist = useWishlist();

  useEffect(() => { api<Genre[]>('/genres').then(setGenres).catch(() => setGenres([])); }, []);
  const update = (name: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(name, value); else next.delete(name);
    if (name !== 'page') next.set('page', '1');
    setParams(next);
  };

  return <>
    <section className="hero"><div><p className="eyebrow">Коллекция университета</p><h1>Найдите книгу, которая изменит ваш следующий семестр</h1><p>Классика, исследования и профессиональная литература — в одном спокойном пространстве.</p></div><div className="hero-stat"><strong>{data?.total ?? '—'}</strong><span>книг в каталоге</span></div></section>
    <section className="catalog-layout"><aside className="filters"><h2>Фильтры</h2>
      <label>Поиск<input type="search" value={params.get('q') || ''} onChange={event => update('q', event.target.value)} placeholder="Название, автор или ISBN" /></label>
      <label>Жанр<select value={params.get('genre') || ''} onChange={event => update('genre', event.target.value)}><option value="">Все жанры</option>{genres.map(genre => <option key={genre.id} value={genre.id}>{genre.name}</option>)}</select></label>
      <label>Сортировка<select value={params.get('sort') || 'title'} onChange={event => update('sort', event.target.value)}><option value="title">По названию</option><option value="year">Сначала новые</option><option value="rating">По рейтингу</option></select></label>
      <label className="check"><input type="checkbox" checked={params.get('available_only') === 'true'} onChange={event => update('available_only', event.target.checked ? 'true' : '')} /> Только доступные</label>
      <button className="button button--ghost" onClick={() => setParams({page:'1', sort:'title'})}>Сбросить</button>
    </aside><div className="catalog-content"><div className="section-head"><div><p className="eyebrow">Каталог</p><h2>{params.get('q') ? `Результаты для «${params.get('q')}»` : 'Все книги'}</h2></div><span>{data?.total ?? 0} найдено</span></div>
      {loading ? <StatePanel kind="loading" title="Загружаем каталог" text="Собираем книги с полок…" /> : error ? <StatePanel kind="error" title="Не удалось загрузить" text={error} action={() => location.reload()} /> : !data?.items.length ? <StatePanel kind="empty" title="Ничего не найдено" text="Попробуйте изменить запрос или сбросить фильтры." /> : <div className="book-grid">{data.items.map(book => <BookCard key={book.id} book={book} onWishlist={item => void wishlist.toggle(item)} isSaved={wishlist.ids.includes(book.id)} />)}</div>}
      {data && data.total > data.size && <nav className="pagination" aria-label="Страницы каталога"><button disabled={data.page === 1} onClick={() => update('page', String(data.page - 1))}>← Назад</button><span>Страница {data.page}</span><button disabled={data.page * data.size >= data.total} onClick={() => update('page', String(data.page + 1))}>Далее →</button></nav>}
    </div></section>
  </>;
}
