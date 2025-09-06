FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
# We're keeping build-essential for any potential compilation needed by Python packages.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to take advantage of Docker layer caching.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files.
# This includes `app/`, `alembic.ini`, and `alembic/`.
# It's assumed your `app/` directory contains `main.py`.
COPY . .

# Create necessary directories for your application's data.
# `logs` and `uploads_data` are added back as they were in the original.
RUN mkdir -p data/chroma uploads_data logs

# Expose the port your application will run on.
EXPOSE 8000

# Set environment variables for Python.
# PYTHONUNBUFFERED=1 ensures logs are immediately flushed.
# PYTHONDONTWRITEBYTECODE=1 prevents the creation of __pycache__ directories.
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


# Define the command to run your application using Uvicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
