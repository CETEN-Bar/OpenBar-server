#!/bin/sh
set -e
poetry run gunicorn "app:create_app()" $([ "$ENV" = "development" ] && echo "--reload")
