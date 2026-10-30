import { render,screen } from '@testing-library/react';import { describe,expect,it } from 'vitest';import { StatePanel } from './StatePanel';
describe('StatePanel',()=>{it('announces an error',()=>{render(<StatePanel kind="error" title="Ошибка" text="Сервис недоступен"/>);expect(screen.getByRole('alert')).toHaveTextContent('Сервис недоступен')})});

