# 2026-VK-EDU-Web-11-Malov-T

**404** — сервис вопросов и ответов

## ДЗ 1 — статическая вёрстка

Список новых вопросов - `public/index.html` 
Вопрос с ответами - `public/question.html` 
Задать вопрос - `public/ask.html` 
Вход - `public/login.html` 
Регистрация - `public/signup.html` 
Настройки профиля - `public/profile.html` 
Базовый шаблон - `public/base.html` 


## Как открыть вёрстку

Откройте `public/index.html` в браузере двойным кликом: установка зависимостей не нужна.

Через Live Server: откройте папку проекта в VS Code, установите расширение **Live Server**, нажмите правой кнопкой на `public/index.html` и выберите **Open with Live Server**.

Альтернатива — из корня проекта выполнить `python3 -m http.server 8000 --directory public` и открыть http://localhost:8000/.

## ДЗ 2 — Django

Восемь страниц доступны через Django. Вопросы и ответы пока хранятся в заглушках, а списки разбиваются на страницы. Вход, регистрация, профиль и отправка форм демонстрируют вёрстку.

### Локальный запуск

Из корня репозитория, с Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
set -a
source ./.env
set +a
python manage.py migrate
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Команда `source ./.env` экспортирует настройки при включённом `set -a`: Django читает переменные окружения, а сам файл автоматически не загружает. Без файла проект также запускается с локальными настройками по умолчанию.

### Запуск через Docker Compose

С запущенным Docker Desktop, из корня репозитория:

```bash
cp -n .env.example .env
docker compose up --build
```

Откройте http://localhost:8000/. Compose читает `.env`, применяет миграции и запускает сервер на порту 8000. Код подключён из рабочей папки, а `media/` хранится в отдельном томе. Если локальный Django уже занял порт 8000, остановите его перед запуском Compose.
