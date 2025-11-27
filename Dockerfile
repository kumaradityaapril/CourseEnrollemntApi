# Use official Python image
FROM python:3.13

# Set working directory
WORKDIR /app

# Copy the whole project
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose default FastAPI port
EXPOSE 8000

# Command to run app (change 'app.main:app' if your entrypoint is different)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
