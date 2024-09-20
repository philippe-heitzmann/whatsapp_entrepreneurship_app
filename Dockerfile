# Use the official Python image.
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

COPY gcs_credentials.json /app/gcs_credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/gcs_credentials.json"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Dockerfile additions

EXPOSE 5005

# Run the script when the container launches
CMD ["python", "./src/whatsapp_bot.py"]
