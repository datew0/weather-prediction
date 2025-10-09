FROM python:3.12-slim-bookworm

# Установить uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app
RUN uv sync

CMD ["uv", "run", "main.py"]