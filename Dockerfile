# Use a multi-stage build to create a distroless image
# Stage 1: Build the application
FROM python:3.11-slim as builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and other necessary files into the container
COPY app/ ./app/

# Stage 2: Create the distroless image
FROM gcr.io/distroless/cc-debian12

# Set the working directory in the container
WORKDIR /app

# Copy the application code and dependencies from the builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

# Command to run the FastAPI app using uvicorn
CMD ["python3.11", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]