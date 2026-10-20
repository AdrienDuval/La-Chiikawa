FROM python:3.12-slim

# same uv version as on your maching 
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv

WORKDIR /app

# 1) install libraries first (cached until uv.lock changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# 2) then copy our code and install it
COPY src ./src
RUN uv sync --locked --no-dev 

CMD ["uv", "run", "--no-sync", "chiikawa"]