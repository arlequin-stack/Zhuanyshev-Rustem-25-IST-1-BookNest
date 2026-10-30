export type Role = 'member' | 'librarian';
export interface Author { id:number; name:string; bio?:string|null }
export interface Genre { id:number; name:string }
export interface Book { id:number; title:string; isbn:string; description:string; year:number; rating:number; copies_total:number; copies_available:number; cover_url?:string|null; author_id:number; author:Author; genres:Genre[] }
export interface BookPage { items:Book[]; total:number; page:number; size:number }
export interface User { id:number; email:string; role:Role; profile?:{full_name:string;phone?:string|null}|null }
export interface Loan { id:number; user_id:number; book_id:number; loaned_at:string; due_date:string; returned_at?:string|null; book:Book }
export interface ApiErrorBody { code?:string; message?:string; detail?:string; details?:unknown; request_id?:string }

