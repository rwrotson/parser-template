# Based on:
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile

# STAGE 1: Build the application
ARG PYTHON_VERSION=3.13.1-bookworm
FROM python:${PYTHON_VERSION} AS builder

# To optimize the build, set the following environment variables, due to:
# https://docs.astral.sh/uv/guides/integration/docker/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install uv by copying the binary from the official distroless Docker image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install the project's dependencies using the lockfile and settings
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Add the rest of the project source code and install it (Installing separately from its dependencies allows optimal layer caching)
COPY ../src README.md LICENSE /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# STAGE 2: Run the application
# It is important to use the image that matches the builder, as the path to the Python executable must be the same
ARG PYTHON_VERSION=3.13.1-bookworm
FROM python:${PYTHON_VERSION} AS runner

# Dependencies for Chrome webdriver
RUN apt update && apt install -y libnss3 libnspr4

# Install Chrome browser
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt clean

# Create a non-root user for security
RUN groupadd --system appgroup && useradd --system --create-home --gid appgroup appuser

# Copy the application from the builder
COPY --from=builder --chown=appuser:appgroup /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DISPLAY=:99

WORKDIR /app

# Switch to the non-root user
USER appuser

# Mount the logs directory as a volume
VOLUME /app/logs
VOLUME /app/media

# Define healthcheck to ensure the application is running
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application by default
CMD ["python", "-m", "app.example"]
# CMD ["sh", "-c", "while true; do sleep 30; done"]  # for testing purposes
