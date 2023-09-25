# Use the official Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the working directory
COPY . .

# Set environment variables for the database connection
ENV POSTGRES_USER=cyberuser
ENV POSTGRES_PASSWORD=cyberpassword
ENV POSTGRES_DB=cyberapi

# Install PostgreSQL
RUN apt-get update && apt-get install -y postgresql

# Start the PostgreSQL service
RUN service postgresql start

## Create the user and database
#RUN su - postgres -c "psql --command \"CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';\""
#RUN su - postgres -c "psql --command \"CREATE DATABASE $POSTGRES_DB WITH OWNER $POSTGRES_USER;\""

# Expose the port for the FastAPI application
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]