# Transaction Guardian API
# CloudWalk Task 3.2

FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY infrastructure/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY code/ ./code/

# Expose port
EXPOSE 8000

# Run API
CMD ["uvicorn", "code.main:app", "--host", "0.0.0.0", "--port", "8000"]
