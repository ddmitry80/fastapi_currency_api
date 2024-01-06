# fastapi_currency_api

# init DB
docker run --name postgres_s_course_project -p 5432:5432 -e POSTGRESS_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=app -d postgres:16.1

# init Test DB
docker run --name postgres_s_course_proj_test -p 5433:5432 -e POSTGRESS_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test -d postgres:16.1
