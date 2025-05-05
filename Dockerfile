FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        musl-dev \
        libpq-dev \
        libmupdf-dev \
        python3-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/static /app/staticfiles

# Collect static files
RUN echo "Collecting static files..." && \
    python manage.py collectstatic --noinput --clear && \
    echo "Static files collected successfully" && \
    ls -la /app/staticfiles/

# Set permissions
RUN chmod +x wait-for-it.sh

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
