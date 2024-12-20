FROM ghcr.io/astral-sh/uv:0.5-debian

ENV DOCKER=1

COPY . /app/

WORKDIR /app/

RUN uv sync

ENTRYPOINT ["uv", "run", "labosphere", "start"]