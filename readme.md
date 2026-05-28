## TeamFinder

TeamFinder — веб-платформа для поиска команды под pet-проекты. Пользователи регистрируются, создают проекты, указывают описание и ссылку на GitHub, присоединяются к чужим инициативам и отмечают интересные проекты в избранном.

### Возможности

- Регистрация и вход по email и паролю, редактирование профиля и смена пароля.
- Автогенерация аватара с первой буквой имени при регистрации.
- Создание и редактирование проектов, закрытие проекта владельцем.
- Участие в проектах и список избранных.
- Каталог участников с фильтрами: авторы избранных проектов, авторы проектов, где вы участник, заинтересованные в ваших проектах, участники ваших проектов.
- Пагинация списков проектов и пользователей.

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

### Что реализовано

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

### Авторы

- **sanechka26** — [GitHub](https://github.com/sanechka26), [aakifev05@gmail.com](mailto:aakifev05@gmail.com)
- Репозиторий: [github.com/sanechka26/team-finder-ad](https://github.com/sanechka26/team-finder-ad)
