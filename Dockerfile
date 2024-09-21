# Use a specific version of Python for consistency
FROM python:3.9 AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Configure Poetry to create virtual environments inside the project directory
RUN poetry config virtualenvs.in-project true

# Copy only the dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Use a smaller base image for the final stage
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv .venv/

# Copy the application code
COPY . .

# Command to run the FastAPI application using Uvicorn
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]