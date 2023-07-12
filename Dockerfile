FROM python:3.11.1

ENV POETRY_HOME=/opt/poetry
ENV PATH=${POETRY_HOME}/bin:${PATH}
ENV DOCKER=1

COPY . /app

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python - --version=$(cat .poetry-version) && \
    poetry install --only main

ENTRYPOINT ["poetry", "run", "labosphere", "start"]