FROM python:3 

ENV IN_DOCKER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

COPY app/pyproject.toml app/poetry.lock /opt/app/

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"
RUN poetry config virtualenvs.create false

WORKDIR /opt/app
RUN poetry install $([ "$ENV" = "production" ] && echo "--no-dev") --no-interaction

COPY app /opt/app/

RUN chmod +x docker-entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]
