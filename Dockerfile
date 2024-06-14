# Build stage
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN groupadd -r celes && useradd --no-log-init -r -g celes celes

RUN chown -R celes:celes /app

USER celes
