# Runbook развёртывания

## Первый запуск

1. Подготовить Ubuntu 24.04 LTS, создать пользователя `booknest`, добавить SSH-ключ и отключить вход root по паролю.
2. Установить Docker Engine, Compose v2, Nginx и certbot. Разрешить UFW только `OpenSSH`, `Nginx Full`.
3. Клонировать репозиторий, выполнить `cp .env.example .env`.
4. Сгенерировать новый `SECRET_KEY`, заменить пароли БД.
5. Выполнить `docker compose up -d --build`; контейнер API сам применит миграции и seed.
6. Проверить `docker compose ps`, `/health`, `/api/docs` и UI.

## Обновление

```bash
git pull --ff-only
docker compose up -d --build
docker compose logs --tail=100 api web
```

Миграции применяются контейнером API до запуска Uvicorn.

## Диагностика

Первые команды при недоступности: `docker compose ps`, `docker compose logs --tail=200`,
`curl -I http://127.0.0.1/health`. Проверить DNS, срок сертификата, свободное место и состояние БД.

## Резервное копирование

```bash
docker compose exec -T db pg_dump -U booknest -d booknest > booknest.sql
docker compose exec -T db psql -U booknest -d booknest_test < booknest.sql
```

## HTTPS

Скопировать `deploy/nginx-https.conf` в `/etc/nginx/sites-available/booknest`, заменить домен,
включить конфигурацию и выполнить `sudo certbot --nginx -d <домен>`. Проверить продление:

```bash
sudo nginx -t
sudo certbot renew --dry-run
curl -I http://<домен>
curl -I https://<домен>/health
```

## Восстановление

```bash
docker compose exec -T db createdb -U booknest booknest_restore
docker compose exec -T db psql -U booknest -d booknest_restore < booknest.sql
docker compose exec -T db psql -U booknest -d booknest_restore -c 'select count(*) from books'
```

В production внешний Nginx/Certbot завершает TLS и проксирует единственный открытый порт web.
PostgreSQL и Uvicorn не публикуются напрямую. Контейнерные журналы ограничены тремя файлами
по 10 МБ, сертификат обновляется timer-ом certbot.

