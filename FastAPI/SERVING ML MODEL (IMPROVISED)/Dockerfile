# Base Image 
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy 
COPY requirements.txt .

# Run
RUN pip install  --no-cache-dir -r requirements.txt

COPY . .

# PORT 
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]