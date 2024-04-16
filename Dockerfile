FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . /app

RUN cd /app/pac2 && ./reset_db.sh

CMD ["poetry", "run", "python", "./pac2/wsgi.py"]
