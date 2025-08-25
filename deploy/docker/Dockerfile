# Use Python 3.13 slim image for ARM64
FROM --platform=linux/arm64 python:3.13-slim

# Install uv for ARM64
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to `/app`
WORKDIR /app

# Copy the lockfile and pyproject.toml into the image
COPY uv.lock pyproject.toml ./

# Copy source code
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-cache

# Run the FastAPI application by default
# Note: "app.main:app" should match your project structure
CMD ["/app/.venv/bin/fastapi", "run", "src/laaj/api/main.py", "--port", "8000", "--host", "0.0.0.0"]