@'
# Habit Tracker — Backend

Backend-сервис для трекера привычек на **FastAPI** с **PostgreSQL** и **SQLAlchemy**.

## Стек

- **Python 3.13**
- **FastAPI** — HTTP API
- **SQLAlchemy 2.x** (sync ORM) — работа с БД
- **PostgreSQL 16** — хранилище
- **Pydantic v2 / pydantic-settings** — схемы и конфиг
- **psycopg 3** — драйвер PostgreSQL
- **Docker Compose** — запуск БД
- **uvicorn** — ASGI-сервер
- **Alembic** — Миграции БД

### Структура проекта

```text
habit_backend/
│
├── 🔌 api/
│   └── routers/
│       └── habits.py          # HTTP-эндпоинты
│
├── ⚙️ service/
│   └── habit.py               # бизнес-логика, commit
│
├── 💾 repositories/
│   └── habit.py               # доступ к БД, flush
│
├── 🗄️ models/
│   └── habits.py              # ORM-модели
│
├── 📋 schemas/
│   └── habits.py              # Pydantic-схемы
│
├── 🐘 db/
│   └── session.py             # engine, SessionLocal, Base
│
├── dependencies.py            # DI (get_habit_service)
├── config.py                  # Settings
├── main.py                    # точка входа
├── requirements.txt
└── .env.example
```

- **Роутеры** — только HTTP: валидация входа, вызов сервиса, ответ.
- **Сервисы** — бизнес-правила, границы транзакций (`commit`), исключения домена.
- **Репозитории** — только доступ к данным (`add`, `flush`, `get`, `delete`).
- **Модели** — маппинг на таблицы.
- **Схемы** — контракт API (request/response).

## API

| Метод    | Путь                       | Описание                              |
|----------|----------------------------|---------------------------------------|
| `GET`    | `/api/habits`              | Список привычек                       |
| `POST`   | `/api/habits`              | Создать привычку (201)                |
| `PATCH`  | `/api/habits/{habit_id}`   | Обновить `checked_today`     |
| `DELETE` | `/api/habits/{habit_id}`   | Удалить привычку (204)                |

Интерактивная документация — Swagger UI: `http://127.0.0.1:8000/docs`.

### Примеры

**Создать привычку**

```bash
curl -X POST http://127.0.0.1:8000/api/habits \
  -H "Content-Type: application/json" \
  -d '{"name": "Читать 20 минут"}'

Список

curl http://127.0.0.1:8000/api/habits

Отметить выполненной

bash
curl -X PATCH http://127.0.0.1:8000/api/habits/<habit_id> \
  -H "Content-Type: application/json" \
  -d '{"checked_today": true}'

Снять отметку

bash
curl -X PATCH http://127.0.0.1:8000/api/habits/<habit_id> \
  -H "Content-Type: application/json" \
  -d '{"checked_today": false}'

Удалить

bash
curl -X DELETE http://127.0.0.1:8000/api/habits/<habit_id>
