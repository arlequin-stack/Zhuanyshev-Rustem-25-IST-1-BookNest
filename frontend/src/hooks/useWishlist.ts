import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import type { Book } from '../types';

const STORAGE_KEY = 'booknest_wishlist';

function readLocalIds(): number[] {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
  catch { return []; }
}

export function useWishlist() {
  const { user, loading: authLoading } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (authLoading) return;
    let active = true;
    setLoading(true);
    setError('');
    const request = user
      ? api<Book[]>('/wishlist')
      : Promise.all(readLocalIds().map(id => api<Book>(`/books/${id}`).catch(() => null))).then(items => items.filter((item): item is Book => item !== null));
    request.then(items => { if (active) setBooks(items); }).catch(reason => { if (active) setError(reason instanceof Error ? reason.message : 'Не удалось загрузить список'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [user, authLoading]);

  const toggle = async (book: Book) => {
    const exists = books.some(item => item.id === book.id);
    if (user) {
      await api(`/wishlist/${book.id}`, { method: exists ? 'DELETE' : 'POST' });
    } else {
      const nextIds = exists ? books.filter(item => item.id !== book.id).map(item => item.id) : [...books.map(item => item.id), book.id];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextIds));
    }
    setBooks(current => exists ? current.filter(item => item.id !== book.id) : [...current, book]);
  };

  return { books, ids: books.map(book => book.id), loading, error, toggle };
}
