#!/bin/sh

touch db.sqlite
python -m alembic upgrade head

python -m gunicorn main:app \
    --bind 0.0.0.0:8001 \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 300