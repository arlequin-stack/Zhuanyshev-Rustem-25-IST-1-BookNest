# BookNest API design

Base URL: `/api/v1`. Формат ошибки: `{code, message, details, request_id}`.

| Ресурс | Метод и путь | Назначение | Коды |
|---|---|---|---|
| Auth | `POST /auth/register` | регистрация | 201, 409, 422 |
| Auth | `POST /auth/token` | вход OAuth2 password flow | 200, 401 |
| Auth | `POST /auth/refresh` | обновление пары access/refresh-токенов | 200, 401 |
| Auth | `GET /auth/me` | текущий пользователь | 200, 401 |
| Books | `GET /books` | поиск, фильтры, сортировка, пагинация | 200, 422 |
| Books | `GET /books/{id}` | карточка | 200, 404 |
| Books | `POST /books` | создание библиотекарем | 201, 401, 403, 409, 422 |
| Books | `PATCH /books/{id}` | частичное обновление | 200, 401, 403, 404 |
| Books | `DELETE /books/{id}` | удаление | 204, 401, 403, 404 |
| Authors | `GET /authors` | список авторов | 200 |
| Authors | `GET /authors/{id}/books` | книги автора | 200, 404 |
| Genres | `GET/POST/PATCH/DELETE /genres` | третий CRUD-ресурс | 200, 201, 204, 403, 404, 409 |
| Wishlist | `GET /wishlist` | сохранённые книги пользователя | 200, 401 |
| Wishlist | `POST/DELETE /wishlist/{book_id}` | добавить или удалить книгу | 201, 204, 401, 404, 409 |
| Loans | `POST /loans` | выдача книги | 201, 401, 404, 409, 422 |
| Loans | `GET /loans/mine` | выдачи текущего читателя | 200, 401 |
| Loans | `POST /loans/{id}/return` | возврат | 200, 401, 404, 409 |

Access-токен живёт 30 минут, refresh-токен — 7 дней (значения настраиваются через окружение).
Refresh-токен имеет отдельный тип и не может быть использован вместо access-токена.

Бизнес-правило: при `copies_available == 0` выдача отклоняется с `409 Conflict`.

