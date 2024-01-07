# fastapi_currency_api

# init DB
```bash
docker run --name postgres_s_course_project -p 5432:5432 -e POSTGRESS_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=app -d postgres:16.1
```

# init Test DB
```bash
docker run --name postgres_s_course_proj_test -p 5433:5432 -e POSTGRESS_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test -d postgres:16.1
```

# Currency Data API
https://apilayer.com/marketplace/currency_data-api#documentation-tab

# Миграция БД
## Анализ изменений в БД и создание миграции
На основе моделей БД в коде, не в БД!!!
```bash
alembic revision --autogenerate -m 'migration_name'
```
## Применение миграции
Изменение DDL в БД
```bash
alembic upgrade head
```

