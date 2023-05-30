# Base image for FastAPI
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Install dependencies
RUN pip install redis

# Copy the FastAPI application code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI application
CMD ["python", "main.py"]