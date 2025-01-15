# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --target /app/dependencies

# Copy application code
COPY app/ ./app/

# Final stage using distroless
FROM gcr.io/distroless/python3-debian12

# Set working directory
WORKDIR /app

# Copy Python dependencies and application code from builder
COPY --from=builder /app/dependencies /app/dependencies
COPY --from=builder /app/app /app/app

# Add dependencies to Python path
ENV PYTHONPATH=/app/dependencies

# Command to run the FastAPI app using uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]