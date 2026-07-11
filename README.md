# Tender Aggregator

Агрегатор торгов + (в разработке) ИИ-ассистент по подготовке заявок.
Стек: Python/FastAPI + Postgres + OpenSearch.

## Статус

Сделано и проверено end-to-end (реальная запись в Postgres → чтение через ORM → отдача через HTTP API):

- Структура проекта (`app/core`, `app/models`, `app/schemas`, `app/api`, `app/services/{parsers,search}`, `app/db`)
- Нормализованная модель данных закупки: `Tender`, `Customer`, `TenderDocument` (`app/models/`)
  — общие поля типизированы и проиндексированы (источник, ОКПД2 через GIN-индекс, регион, даты, цена),
  специфика конкретного источника уходит в `raw_data` (JSONB), чтобы не переделывать схему при добавлении новой площадки
- Alembic-миграции настроены на модели (`alembic/env.py`), первая миграция сгенерирована и применена
- Базовый API: `GET /api/v1/tenders`, `GET /api/v1/tenders/{id}`, `GET /health`
- `docker-compose.yml`: Postgres + OpenSearch + api-сервис
- **Парсер ЕИС** (`app/services/parsers/eis/`): SOAP-клиент к сервису отдачи информации ЕИС
  (пришёл на смену закрытому с 01.01.2025 FTP), разбор XML-извещений, upsert в БД.
  Вся цепочка (сборка запроса → разбор ответа → распаковка архива → парсинг XML → запись в БД
  с дедупликацией) проверена end-to-end с эмулированным ответом ЕИС на реальном Postgres.

  **Известное ограничение и как его обошли:** с 6 июля 2025 ЕИС требует ГОСТ-TLS для этого
  сервиса, который стандартные HTTP-клиенты (httpx, curl, requests) устанавливать не умеют.
  Решение, подтверждённое вживую на этом проекте: КриптоПро CSP на Linux/macOS ставится
  вместе со своим `curl` (обычно `/opt/cprocsp/bin/curl`), пересобранным с поддержкой ГОСТ —
  реальный запрос через него к `int.zakupki.gov.ru` успешно получил ответ (HTTP 200, WSDL).
  Клиент (`client.py`) умеет вызывать этот curl как subprocess вместо httpx — достаточно
  указать путь в `.env`:
  ```
  EIS_CURL_BINARY=/opt/cprocsp/bin/curl
  ```
  Логика сборки curl-команд (SOAP-запрос и скачивание архива) проверена на подменённом
  `subprocess.run` — команды и параметры собираются верно. **Полный цикл с реальным сервисом
  (включая парсинг настоящего архива) пока не пройден** — это следующий шаг.

  Старый адрес `int44.zakupki.gov.ru` отключён с 04.10.2025 — актуальный `int.zakupki.gov.ru`,
  он уже прописан в `.env.example` по умолчанию.
  ```bash
  python -m app.services.parsers.eis.sync --region 77 --date 2026-07-08
  ```

Не сделано (следующие шаги):

- Индексация в OpenSearch и поиск через него (`app/services/search/`) — пока листинг идёт напрямую из Postgres
- Планировщик регулярной синхронизации ЕИС (сейчас — только ручной запуск по региону/дате)
- Аутентификация, уведомления, ИИ-ассистент — не начаты

## Запуск (докер)

```bash
cp .env.example .env
docker compose up --build
```

API будет на `http://localhost:8000`, документация — `http://localhost:8000/docs`.

## Запуск миграций вручную

```bash
docker compose exec api alembic upgrade head
```

## Локальная разработка без докера

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://tender:tender@localhost:5432/tender_aggregator"
alembic upgrade head
uvicorn app.main:app --reload
```
