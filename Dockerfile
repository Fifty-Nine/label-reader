# --- Stage 1: Build the Frontend ---
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend

# Install build dependencies
# We copy package.json first to leverage Docker cache
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Final Image ---
FROM python:3.11-slim
WORKDIR /app/backend

# Install system dependencies (needed for poetry)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy backend dependency files
COPY backend/pyproject.toml backend/poetry.lock ./

# Copy backend source
COPY backend/app/ ./app/

RUN poetry config virtualenvs.create false \
    && poetry install --without dev


# Copy frontend build from stage 1 to the static directory
# This matches the STATIC_DIR=static configuration in main.py
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# Environment variables
# OLLAMA_HOST can be overridden at runtime
ENV OLLAMA_HOST=https://ollama.home.trprince.com
ENV STATIC_DIR=static

# Expose port 8000
EXPOSE 8000

# Start the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
