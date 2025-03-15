#!/bin/bash

while ! nc -z db 5432; do
  echo "Waiting for database..."
  sleep 1
done

sleep 5

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
