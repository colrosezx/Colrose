# syntax=docker/dockerfile:1
FROM python:3.9-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies as the new user
COPY --chown=appuser:appgroup requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# System dependencies - can be run as root
RUN apt-get update && apt-get install -y postgresql-client

# Copy backend code as the new user
COPY --chown=appuser:appgroup ./backend /app/

# Copy and set permissions for entrypoint
COPY --chown=appuser:appgroup backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to the non-root user for running the application
USER appuser

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
