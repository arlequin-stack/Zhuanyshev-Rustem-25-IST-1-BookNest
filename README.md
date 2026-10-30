<div align="center">

# BookNest

### Университетская библиотека и книжный клуб

Full-stack приложение по курсу «Современные веб-технологии»: каталог книг,
личный кабинет читателя и панель управления библиотекаря.

[![Открыть сайт](https://img.shields.io/badge/ОТКРЫТЬ_САЙТ-BookNest-22C55E?style=for-the-badge&logo=render&logoColor=white)](https://booknest-library-e0nk.onrender.com)
[![Swagger API](https://img.shields.io/badge/SWAGGER-API_DOCS-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://booknest-library-e0nk.onrender.com/api/docs)
[![CI](https://img.shields.io/github/actions/workflow/status/arlequin-stack/booknest-library/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/arlequin-stack/booknest-library/actions)

</div>

## Использованные языки

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)

## Frontend

![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite_6-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=reactrouter&logoColor=white)
![React Hook Form](https://img.shields.io/badge/React_Hook_Form-EC5990?style=for-the-badge&logo=reacthookform&logoColor=white)
![Zod](https://img.shields.io/badge/Zod-3E67B1?style=for-the-badge&logo=zod&logoColor=white)

## Backend и API

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6BA81E?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

## База данных и развёртывание

![PostgreSQL](https://img.shields.io/badge/PostgreSQL_17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Render](https://img.shields.io/badge/Render-000000?style=for-the-badge&logo=render&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

## Тестирование и качество кода

![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Vitest](https://img.shields.io/badge/Vitest-6E9F18?style=for-the-badge&logo=vitest&logoColor=white)
![ESLint](https://img.shields.io/badge/ESLint-4B32C3?style=for-the-badge&logo=eslint&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

## Возможности

- каталог с поиском, фильтрацией, сортировкой и пагинацией;
- подробные карточки книг и серверный список желаемого;
- регистрация, вход и автоматическое обновление сессии через refresh-токен;
- роли `member` и `librarian` с разграничением доступа;
- панель библиотекаря и CRUD для книг, авторов и жанров;
- выдача и возврат книг с контролем доступных экземпляров;
- единый формат ошибок API и интерактивная OpenAPI-документация;
- светлая и тёмная темы, адаптивная вёрстка и доступные формы.

## Рабочая версия

| Ресурс | Ссылка |
| --- | --- |
| Сайт | [booknest-library-e0nk.onrender.com](https://booknest-library-e0nk.onrender.com) |
| Swagger UI | [API documentation](https://booknest-library-e0nk.onrender.com/api/docs) |
| Healthcheck | [`/health`](https://booknest-library-e0nk.onrender.com/health) |

На бесплатном тарифе Render сервис засыпает после бездействия, поэтому первое открытие
может занять около минуты.

## Архитектура и данные

React-приложение и FastAPI работают в одном production-контейнере. FastAPI обслуживает
REST API и собранный frontend, а PostgreSQL хранит данные. Перед запуском автоматически
применяются миграции Alembic и добавляются демонстрационные записи.

База содержит восемь таблиц в 3NF: `authors`, `books`, `genres`, `book_genres`, `users`,
`profiles`, `loans`, `wishlist`. Реализованы связи 1:1, 1:N и M:N, ограничения и индексы.
DDL, seed, 12 SQL-запросов и EXPLAIN находятся в [`db/`](db/README.md).

## Быстрый запуск через Docker

```bash
cp .env.example .env
docker compose up -d --build
```

- Сайт: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/api/docs`

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

Автоматический набор содержит 26 backend-тестов и 2 frontend-теста. GitHub Actions
дополнительно проверяет обе части приложения и сборку Docker-образов.

## Демонстрационный вход

- E-mail: `librarian@example.com`
- Пароль: `Library123`
- Роль: библиотекарь

Читателя можно зарегистрировать самостоятельно на странице `/register`.

## Лабораторные работы

1. Семантическая HTML-разметка и доступность.
2. Адаптивный CSS, дизайн-токены и тёмная тема.
3–6. TypeScript, интерактивный каталог, React, Router и формы.
7–10. FastAPI, PostgreSQL, JWT, интеграция и автоматические тесты.
11–12. Docker, Nginx, CI/CD и публикация на Render.

Полная карта требований находится в [`docs/labs.md`](docs/labs.md), аудит безопасности —
в [`docs/security-review.md`](docs/security-review.md), инструкции развёртывания —
в [`docs/render-free.md`](docs/render-free.md).
