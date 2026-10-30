# Карта этапов лабораторных

- ЛР 1–2: семантика, доступность, адаптивный CSS и токены — `frontend/index.html`, `src/components`, `src/styles.css`.
- ЛР 3–4: фильтры, URL-состояние, wishlist, async API и четыре состояния UI — `CatalogPage`, `useBooks`, `api/client`.
- ЛР 5–6: React, TypeScript, Router, Context, Zod-формы и защищённые маршруты — `frontend/src`.
- ЛР 7: FastAPI CRUD и OpenAPI — `backend/app/routers`.
- ЛР 8: PostgreSQL, 3NF, SQLAlchemy, 3 миграции — `models.py`, `alembic/versions`.
- ЛР 9: bcrypt, JWT access/refresh, ротация сессии, роли и владение выдачей — `security.py`, `deps.py`, `routers/auth.py`.
- ЛР 10: интеграция и тесты — Vite proxy, Vitest, pytest.
- ЛР 11: Docker, Compose, healthcheck, Nginx — Dockerfile, `.dockerignore`,
  `docker-compose.yml`, `nginx.conf`. Локальная проверка кода выполнена; для зачёта
  нужен фактический `docker compose up -d --build` на машине с Docker.
- ЛР 12: инструкции VPS/HTTPS/backup — `docs/deployment.md`,
  `deploy/nginx-https.conf`. Для зачёта нужны VPS, DNS-имя и фактическая проверка HTTPS,
  backup/restore и повторного развёртывания.

