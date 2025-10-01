FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Expose port
EXPOSE 8000

# Create non-root user for security
RUN useradd -m -u 1000 clipsmart && chown -R clipsmart:clipsmart /app
USER clipsmart

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["uvicorn", "backend.processing.main:app", "--host", "0.0.0.0", "--port", "8000"]