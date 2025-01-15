# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Final stage using distroless
FROM gcr.io/distroless/cc-debian12

# Copy Python installation from builder
COPY --from=builder --chown=nonroot:nonroot /usr/local /usr/local

# Copy virtual environment
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

# Copy application code
COPY --from=builder --chown=nonroot:nonroot /app/app /app/app

# Set the Python path to include the virtual environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Use nonroot user
USER nonroot

# Command to run the FastAPI app
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]