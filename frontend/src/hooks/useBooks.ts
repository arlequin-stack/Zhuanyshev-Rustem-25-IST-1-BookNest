import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { BookPage } from '../types';
export function useBooks(query:string){
 const [data,setData]=useState<BookPage|null>(null);const [loading,setLoading]=useState(true);const [error,setError]=useState('');
 useEffect(()=>{const controller=new AbortController();setLoading(true);setError('');api<BookPage>(`/books?${query}`,{signal:controller.signal}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(e.message)}).finally(()=>setLoading(false));return()=>controller.abort()},[query]);
 return {data,loading,error};
}

