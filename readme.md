## TeamFinder

Платформа для поиска команды в pet‑проекты.

### Стек

- Python 3.12
- Django 5.2
- PostgreSQL 16
- Docker / docker-compose

### Быстрый старт (Docker)

1) Создайте `.env`:

```bash
copy .env_example .env
```

2) Запустите всё:

```bash
docker compose up --build
```

3) Откройте:

- `http://localhost:8000/` — приложение

### Локальный запуск без Docker (опционально)

Если хотите запускать Django локально, укажите в `.env`:

- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432` (или другой порт, если меняли проброс)

Дальше:

```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Что реализовано (вариант 1)

- Кастомный `User` (email как username) + генерация аватара с первой буквой имени.
- `Project` + участие в проектах.
- **Избранное**: `POST /projects/<id>/toggle-favorite/` и страница `GET /projects/favorites/`.
- Фильтры пользователей на `GET /users/list/?filter=...` (4 типа, как в шаблонах).

### Переменные окружения

Файл `.env` создаётся из `.env_example`.

- **`DJANGO_SECRET_KEY`**: секретный ключ Django
- **`DJANGO_DEBUG`**: `True/False`
- **`DJANGO_ALLOWED_HOSTS`**: список хостов через запятую (по умолчанию `localhost,127.0.0.1`)
- **`POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_HOST/POSTGRES_PORT`**: параметры БД
- **`TASK_VERSION`**: выбор набора шаблонов (`templates_var1/2/3`). Для варианта 1 — `1`.

### Автор

Заполните этот блок своими данными перед сдачей (ФИО/ник/контакты).

