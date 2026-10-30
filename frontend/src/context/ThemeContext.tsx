import { createContext,useContext,useEffect,useState,type ReactNode } from 'react';
const ThemeContext=createContext({theme:'light',toggle:()=>{}});
export function ThemeProvider({children}:{children:ReactNode}){const[theme,setTheme]=useState(()=>localStorage.getItem('booknest_theme')||'light');useEffect(()=>{document.documentElement.dataset.theme=theme;localStorage.setItem('booknest_theme',theme)},[theme]);return <ThemeContext.Provider value={{theme,toggle:()=>setTheme(v=>v==='light'?'dark':'light')}}>{children}</ThemeContext.Provider>}
export const useTheme=()=>useContext(ThemeContext);

