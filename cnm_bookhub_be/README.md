# cnm_bookhub_be

This project was generated using fastapi_template.

## UV

This project uses uv. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
uv sync --locked
uv run -m cnm_bookhub_be
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about uv here: https://docs.astral.sh/ruff/

## Setup với pip (cho developers không dùng uv)

Dự án này hỗ trợ cả `uv` và `pip`. Nếu bạn muốn dùng `pip` thay vì `uv`:

### Tạo file requirements (chỉ cần làm 1 lần khi có thay đổi dependencies)

Nếu bạn đã có `uv` và muốn tạo lại file requirements sau khi cập nhật dependencies:

```bash
# Tạo requirements.txt cho production dependencies
uv pip compile pyproject.toml -o requirements.txt

# Tạo requirements-dev.txt cho dev dependencies (bao gồm cả production)
uv pip compile pyproject.toml --group dev -o requirements-dev.txt
```

### Setup dự án với pip

1. Tạo virtual environment (khuyến nghị):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Cài đặt dependencies:

**Cho production:**
```bash
pip install -r requirements.txt
```

**Cho development (khuyến nghị):**
```bash
pip install -r requirements-dev.txt
```

3. Chạy dự án:
```bash
python -m cnm_bookhub_be
```

## Docker

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `uv.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

## Project structure

```bash
$ tree "cnm_bookhub_be"
cnm_bookhub_be
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifespan.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here. 

All environment variables should start with "CNM_BOOKHUB_BE_" prefix.

For example if you see in your "cnm_bookhub_be/settings.py" a variable named like
`random_parameter`, you should provide the "CNM_BOOKHUB_BE_RANDOM_PARAMETER" 
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `cnm_bookhub_be.settings.Settings.Config`.

An example of .env file:
```bash
CNM_BOOKHUB_BE_RELOAD="True"
CNM_BOOKHUB_BE_PORT="8000"
CNM_BOOKHUB_BE_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* mypy (validates types);
* ruff (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "3306:3306" -e "MYSQL_PASSWORD=cnm_bookhub_be" -e "MYSQL_USER=cnm_bookhub_be" -e "MYSQL_DATABASE=cnm_bookhub_be" -e ALLOW_EMPTY_PASSWORD=yes mysql:8.4
```


2. Run the pytest.
```bash
pytest -vv .
```
