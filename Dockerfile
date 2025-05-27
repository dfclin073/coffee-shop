# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /fast

# Install dependencies
RUN --mount=type=cache,target=/home/hexdef/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image
ADD . /fast

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
CMD ["uv", "run", "uvicorn", "--host=0.0.0.0", "fast.main:app"]
# docker run --rm -it -p 8000:8000 -e DATABASE_URL="mongodb://172.21.123.86:27017/" backend