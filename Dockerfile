FROM python:3.10-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m -r appuser && \
    chown appuser:appuser /app

# Create and activate virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy data first
COPY src/data/df_top.csv /app/src/data/

# Copy application files
COPY src/app.py /app/src/
COPY requirements.txt /app/

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--log-level", "debug", "--timeout", "120", "--workers", "1", "src.app:server"]