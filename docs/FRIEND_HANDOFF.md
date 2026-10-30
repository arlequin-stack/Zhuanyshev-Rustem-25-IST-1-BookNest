# BookNest — инструкция для завершения публикации и сдачи

Локальный код, тесты, Dockerfile, Compose, CI, SQL-артефакты и документация уже готовы.
Осталось создать удалённый GitHub-репозиторий, получить зелёный CI и развернуть проект на VPS.

## 0. Что потребуется

- аккаунт GitHub с подтверждённой почтой;
- VPS с Ubuntu 24.04 LTS, минимум 1 vCPU, 1–2 ГБ RAM и публичным IPv4;
- домен или поддомен с возможностью создать DNS-запись `A`;
- SSH-ключ на компьютере;
- Docker Desktop для локальной проверки — желательно, но необязательно, если проверка выполняется на VPS.

Никогда не отправлять другому человеку и не коммитить: `.env`, приватный SSH-ключ,
пароли VPS/БД, `SECRET_KEY`, дамп production-базы.

## 1. Проверка проекта до GitHub

```bash
cd "/Users/markdubinin/Documents/Проекты/Rustem_biblio"
git status --short
git check-ignore -v backend/booknest.db frontend/node_modules backend/.venv frontend/dist

cd frontend
npm ci
npm run lint
npm run build
npm test -- --run
npm audit --omit=dev

cd ../backend
source .venv/bin/activate
SECRET_KEY=test-only-secret-key-not-for-production pytest -q
deactivate
cd ..
```

Ожидаемый результат: ESLint без ошибок, frontend build успешен, 2 frontend-теста и
24 backend-теста проходят, production audit сообщает 0 уязвимостей.

## 2. GitHub и первый Pull Request

1. Зарегистрироваться на GitHub, подтвердить почту и включить двухфакторную аутентификацию.
2. На GitHub создать **пустой** репозиторий `booknest`; не добавлять README, `.gitignore` или License.
3. Настроить имя и подтверждённый e-mail Git:

```bash
git config user.name "ИМЯ СТУДЕНТА"
git config user.email "ПОДТВЕРЖДЕННЫЙ_EMAIL_GITHUB"
```

4. Добавить пустой базовый коммит в `main`, затем вынести проект в отдельную ветку:

```bash
git commit --allow-empty -m "chore: initialize BookNest repository"
git remote add origin https://github.com/USERNAME/booknest.git
git push -u origin main
git switch -c lab-12/finalize
git add .
git status --short
git commit -m "feat: complete BookNest full-stack application"
git push -u origin lab-12/finalize
```

Перед коммитом убедиться, что в списке нет `.env`, `booknest.db`, `.venv`, `node_modules`,
`dist`, приватных ключей или дампов БД.

5. На GitHub открыть Pull Request `lab-12/finalize` → `main`. В описании указать:

- что реализовано;
- команды проверки;
- результаты тестов;
- локальные скриншоты;
- ссылку на `docs/security-review.md` и `docs/deployment.md`.

6. Дождаться зелёного GitHub Actions. Workflow должен выполнить ESLint, Ruff, frontend build,
Vitest, pytest и сборку двух Docker-образов. При ошибке открыть красный job, исправить причину,
сделать новый commit и push в ту же ветку.
7. После зелёного CI объединить PR кнопкой **Squash and merge** или обычным merge согласно правилам преподавателя.

Не создавать задним числом фиктивные 12 PR и искусственную историю. Если преподаватель требует
отдельные исторические PR каждой лабораторной, честно сообщить, что проект импортирован как
консолидированная итоговая версия, и согласовать формат сдачи.

## 3. Локальная проверка Docker

Установить Docker Desktop. В корне проекта:

```bash
cp .env.example .env
openssl rand -hex 32
openssl rand -hex 24
```

Первое значение поместить в `SECRET_KEY`, второе — в `POSTGRES_PASSWORD`. Так как пароль hex,
его можно без URL-кодирования подставить в `DATABASE_URL`:

```dotenv
POSTGRES_DB=booknest
POSTGRES_USER=booknest
POSTGRES_PASSWORD=СЛУЧАЙНЫЙ_HEX_ПАРОЛЬ
DATABASE_URL=postgresql+psycopg://booknest:СЛУЧАЙНЫЙ_HEX_ПАРОЛЬ@db:5432/booknest
SECRET_KEY=СЛУЧАЙНЫЙ_64_СИМВОЛЬНЫЙ_HEX
ACCESS_TOKEN_MINUTES=30
REFRESH_TOKEN_DAYS=7
CORS_ORIGINS=http://localhost:8080
VITE_API_URL=/api/v1
```

Проверка с нуля — только до появления ценных данных:

```bash
docker compose config -q
docker compose down -v
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 api web db
curl -f http://127.0.0.1:8080/health
```

Открыть:

- `http://127.0.0.1:8080/books`;
- `http://127.0.0.1:8080/api/docs`;
- прямую ссылку `http://127.0.0.1:8080/books/2` и обновить страницу.

Проверить сохранение данных:

```bash
docker compose down
docker compose up -d
```

После `down` данные должны сохраниться. Команда `down -v` удаляет том PostgreSQL и все данные.

## 4. Подготовка VPS

При регистрации у провайдера выбрать Ubuntu 24.04 LTS. Платные тарифы и привязку карты
подтверждает владелец аккаунта. На сервере сначала создать обычного пользователя и только потом
отключать root/password login, иначе можно потерять доступ.

```bash
ssh root@SERVER_IP
adduser booknest
usermod -aG sudo booknest
mkdir -p /home/booknest/.ssh
cp /root/.ssh/authorized_keys /home/booknest/.ssh/authorized_keys
chown -R booknest:booknest /home/booknest/.ssh
chmod 700 /home/booknest/.ssh
chmod 600 /home/booknest/.ssh/authorized_keys
```

Открыть второй терминал и проверить `ssh booknest@SERVER_IP`. Только после успешной проверки
можно отключить вход root по паролю в `/etc/ssh/sshd_config`:

```text
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
```

Затем:

```bash
sudo sshd -t
sudo systemctl reload ssh
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl git nginx ufw
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

Docker Engine и Compose устанавливать по официальной инструкции Docker для Ubuntu. Проверить:

```bash
sudo systemctl status docker --no-pager
sudo docker run --rm hello-world
docker compose version
sudo usermod -aG docker booknest
```

После добавления в группу выйти из SSH и войти снова.

## 5. DNS

В панели домена создать запись:

```text
Тип: A
Имя: booknest (или @)
Значение: SERVER_IP
TTL: 300
```

Проверить с компьютера:

```bash
dig +short booknest.example.edu
```

Команда должна вернуть IP сервера. До этого Certbot запускать нельзя.

## 6. Развёртывание приложения

На VPS:

```bash
sudo mkdir -p /opt/booknest
sudo chown booknest:booknest /opt/booknest
git clone https://github.com/USERNAME/booknest.git /opt/booknest
cd /opt/booknest
cp .env.example .env
openssl rand -hex 32
openssl rand -hex 24
nano .env
```

Заполнить `.env` production-секретами и доменом в `CORS_ORIGINS=https://booknest.example.edu`.
Не использовать секрет из локальной разработки.

В `docker-compose.yml` привязать web только к loopback сервера:

```yaml
ports:
  - "127.0.0.1:8080:80"
```

Затем:

```bash
docker compose config -q
docker compose up -d --build
docker compose ps
docker compose logs --tail=150 api web db
curl -f http://127.0.0.1:8080/health
```

API и PostgreSQL не должны иметь опубликованных портов.

## 7. Nginx и HTTPS

Сначала создать HTTP-конфигурацию `/etc/nginx/sites-available/booknest`:

```nginx
server {
    listen 80;
    server_name booknest.example.edu;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/booknest /etc/nginx/sites-enabled/booknest
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
curl -I http://booknest.example.edu
```

Установить Certbot способом, рекомендованным официальным selector-ом Certbot для Ubuntu/Nginx,
затем выполнить:

```bash
sudo certbot --nginx -d booknest.example.edu
sudo certbot renew --dry-run
curl -I http://booknest.example.edu
curl -I https://booknest.example.edu/health
```

Первый запрос должен перенаправляться на HTTPS. После получения сертификата добавить в HTTPS
server-блок заголовки из `deploy/nginx-https.conf`, выполнить `sudo nginx -t` и reload.

## 8. Демонстрационные аккаунты и полный сценарий

Seed создаёт библиотекаря:

```text
librarian@example.com / Library123
```

Через страницу `/register` создать читателя, например:

```text
reader@example.com / Reader123
```

Пройти по публичному HTTPS-адресу:

1. регистрация читателя;
2. вход читателя;
3. поиск и фильтр жанра;
4. добавление книги в wishlist;
5. выдача и возврат книги;
6. выход;
7. вход библиотекаря;
8. создание книги;
9. редактирование книги;
10. просмотр всех выдач.

Проверить также 403 для читателя на операции библиотекаря, 404 на чужую выдачу и 409 при
отсутствии свободных экземпляров.

## 9. Backup и восстановление

```bash
cd /opt/booknest
mkdir -p backups
docker compose exec -T db pg_dump -U booknest -d booknest > backups/booknest.sql
test -s backups/booknest.sql && echo "backup OK"

docker compose exec -T db createdb -U booknest booknest_restore
docker compose exec -T db psql -U booknest -d booknest_restore < backups/booknest.sql
docker compose exec -T db psql -U booknest -d booknest_restore -c 'SELECT count(*) FROM books;'
docker compose exec -T db dropdb -U booknest booknest_restore
```

Не добавлять `backups/` в Git. При необходимости дополнить `.gitignore` строкой `backups/`.

## 10. Повторное развёртывание

После небольшого изменения, commit, PR и merge:

```bash
cd /opt/booknest
git pull --ff-only
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 api web
curl -f https://booknest.example.edu/health
```

Контейнер API автоматически выполняет `alembic upgrade head` перед запуском.

## 11. Что добавить в README перед сдачей

- публичный HTTPS URL;
- URL GitHub-репозитория и финального PR;
- демо-аккаунты двух ролей;
- фактические команды запуска;
- вывод тестов и дату последней проверки;
- краткую схему данных и ссылку на `db/README.md`.

Сделать commit `docs: add production deployment evidence`, push и дождаться зелёного CI.

## 12. Доказательства для преподавателя

Сохранить в `docs/evidence/` без секретов:

- `github-ci.png` — зелёный Actions;
- `compose-ps.txt` — вывод `docker compose ps`;
- `https.png` — публичный URL и замок сертификата;
- `lighthouse.pdf` или скриншот Accessibility/Performance;
- `backup-restore.txt` — команды и результат восстановления;
- `api-tests.txt` и `frontend-tests.txt`;
- ссылка на финальный PR;
- ссылка на публичное приложение.

## 13. Финальная проверка секретов

```bash
git status --short
git log --all --full-history -- .env
git grep -n "SECRET_KEY=" || true
git grep -n "localhost:8000\|127.0.0.1:8000" -- 'frontend/src/**' || true
git grep -n "dangerouslySetInnerHTML\|create_all" -- 'frontend/src/**' 'backend/app/**' || true
```

История `.env` должна быть пустой. Допустимы только названия переменных и безопасные значения
в `.env.example`; production-секреты не должны появляться ни в commit, ни в PR, ни на скриншотах.

## 14. Отправка в EKTU

В ответе на задание указать:

1. URL GitHub-репозитория;
2. URL финального Pull Request;
3. публичный HTTPS URL;
4. демо-аккаунты читателя и библиотекаря;
5. краткий список реализованных лабораторных;
6. результаты тестов и CI;
7. `AI_USAGE.md` как декларацию использования AI.

Перед финальной отправкой ещё раз открыть все ссылки в приватном окне. Саму кнопку отправки
на учебном портале нажимает студент после проверки текста и приложений.
