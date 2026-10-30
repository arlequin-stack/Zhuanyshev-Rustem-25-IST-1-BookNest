import type { ApiErrorBody } from '../types';
const baseUrl = import.meta.env.VITE_API_URL || '/api/v1';
export class ApiError extends Error { constructor(public status:number, public body:ApiErrorBody){super(body.message||body.detail||'Ошибка запроса')} }
interface TokenPair { access_token:string; refresh_token:string; token_type:string }
async function request<T>(path:string, init:RequestInit={}, canRefresh=true):Promise<T>{
  const token=localStorage.getItem('booknest_token');
  const headers=new Headers(init.headers); if(!(init.body instanceof FormData)) headers.set('Content-Type','application/json'); if(token) headers.set('Authorization',`Bearer ${token}`);
  const response=await fetch(`${baseUrl}${path}`,{...init,headers});
  if(response.status===401&&canRefresh&&localStorage.getItem('booknest_refresh')){const refreshResponse=await fetch(`${baseUrl}/auth/refresh`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:localStorage.getItem('booknest_refresh')})});if(refreshResponse.ok){const pair=await refreshResponse.json() as TokenPair;localStorage.setItem('booknest_token',pair.access_token);localStorage.setItem('booknest_refresh',pair.refresh_token);return request<T>(path,init,false)}}
  if(!response.ok){let body:ApiErrorBody={message:'Сервис временно недоступен'};try{body=await response.json()}catch{body={message:'Сервис временно недоступен'}} if(response.status===401){localStorage.removeItem('booknest_token');localStorage.removeItem('booknest_refresh');if(!location.pathname.startsWith('/login'))location.assign(`/login?next=${encodeURIComponent(location.pathname+location.search)}`)} throw new ApiError(response.status,body)}
  if(response.status===204)return undefined as T; return response.json() as Promise<T>;
}
export function api<T>(path:string,init:RequestInit={}):Promise<T>{return request<T>(path,init)}

