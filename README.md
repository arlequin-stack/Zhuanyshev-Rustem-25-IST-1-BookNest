# BookNest

Учебное full-stack приложение книжного клуба по накопительному ТЗ курса «Современные веб-технологии».

## Стек

- Frontend: React 19, Vite 6, TypeScript, React Router, React Hook Form, Zod.
- Backend: FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, JWT, bcrypt.
- Data: PostgreSQL 17, связи 1:1, 1:N и M:N.
- Delivery: Docker Compose, multi-stage frontend build, Nginx reverse proxy.

## Схема данных

Восемь таблиц в 3NF: `authors`, `books`, `genres`, `book_genres`, `users`, `profiles`,
`loans`, `wishlist`. Реализованы связи 1:N, M:N и 1:1, ограничения и индексы.
DDL, seed, 12 запросов и EXPLAIN находятся в [`db/`](db/README.md).

## Возможности

- каталог с поиском, фильтрацией, сортировкой и пагинацией;
- карточка книги и серверный список желаемого;
- регистрация, вход и автоматическое обновление сессии через refresh-токен;
- роли `member` и `librarian`, отдельная панель управления каталогом;
- CRUD книг, авторов и жанров;
- выдача и возврат книг;
- бизнес-правило: нельзя выдать книгу без свободного экземпляра (`409 Conflict`);
- единый формат ошибок API и OpenAPI-документация.

## Запуск Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Открыть `http://localhost:8080`. Swagger UI: `http://localhost:8080/api/docs`.

## Бесплатная публикация

Проект подготовлен к бесплатному запуску на Render без отдельного Ubuntu-сервера.
React, FastAPI и миграции упакованы в один контейнер, а PostgreSQL создаётся автоматически
из `render.yaml`. Пошаговая инструкция: [`docs/render-free.md`](docs/render-free.md).

## Локальная разработка

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend (Python 3.12+):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Тесты

```bash
cd backend && pytest -q
cd frontend && npm test -- --run
cd frontend && npm run lint
```

## Переменные окружения

См. `.env.example`. Реальный `.env` не должен попадать в Git.

## Учётные записи демонстрации

После применения миграций выполните `python -m app.seed`. Демо-аккаунты:

- библиотекарь: `librarian@example.com` / `Library123`;
- читателя можно создать через страницу `/register`.

Демо-пароль предназначен только для локальной проверки. В production используйте
отдельный безопасный процесс создания библиотекаря и смените все секреты.

## Этапы лабораторных

1. Семантическая разметка и доступность — реализованы в React-компонентах и формах.
2. Адаптивный CSS, дизайн-токены и тёмная тема — `frontend/src/styles.css`.
3–6. Интерактивный каталог, API-слой, React, Router и формы — `frontend/src`.
7–10. FastAPI, PostgreSQL, JWT, интеграция и тесты — `backend`.
11–12. Docker, Nginx и подготовка к VPS — корневой `docker-compose.yml`, Dockerfile и `nginx.conf`.

Полная карта требований: `docs/labs.md`; аудит безопасности: `docs/security-review.md`;
эксплуатационный runbook: `docs/deployment.md`. Локальный автоматический набор содержит
24 backend-теста и 2 клиентских теста.

