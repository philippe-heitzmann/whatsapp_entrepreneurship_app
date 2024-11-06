#!/bin/bash

# ---------------------------
# WhatsApp Chatbot Deployment Script
# ---------------------------
# This script builds and runs a Docker container named "whatsapp-chatbot" for a WhatsApp chatbot application.
# If a container with the same name is already running, it will be stopped and removed.
# Additionally, it uses ngrok to expose the service for external access, with a URL that can be used in Twilio's configuration.

# Set the working directory to the folder where the script is located
SCRIPT_DIR=$(dirname "$0")
ROOT_DIR=$(realpath "$SCRIPT_DIR/../../")

# Define the container name and image
CONTAINER_NAME="whatsapp-chatbot"
IMAGE_NAME="whatsapp-business-plan-bot"
NGROK_URL="virtual-assistant-440002.ngrok.app"
# Logging function for better readability
log() {
    echo "[INFO] $1"
}

# Check if a container with the specified name is already running
log "Checking for any existing container named $CONTAINER_NAME..."
EXISTING_CONTAINER=$(docker ps -aq -f name=$CONTAINER_NAME)

if [ -n "$EXISTING_CONTAINER" ]; then
    log "Container $CONTAINER_NAME is already running. Stopping and removing it..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    log "Existing container stopped and removed."
else
    log "No existing container named $CONTAINER_NAME found."
fi

# Build the Docker image
log "Building Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME "$ROOT_DIR"
if [ $? -eq 0 ]; then
    log "Docker image built successfully."
else
    log "Error building Docker image."
    exit 1
fi

# Run the Docker container with specified name, mount credentials, and expose port 5000
log "Running Docker container named $CONTAINER_NAME from image: $IMAGE_NAME..."
docker run -d --name $CONTAINER_NAME --env-file=./env/app.env -p 5006:5006 $IMAGE_NAME
if [ $? -eq 0 ]; then
    log "Docker container $CONTAINER_NAME is running."
else
    log "Error running Docker container."
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    log "ngrok could not be found. Please install it from https://ngrok.com/download."
    exit 1
fi

# Run ngrok to expose the local Flask service running in Docker
log "Starting ngrok to expose port 5006..."
ngrok http --url=$NGROK_URL 5006 > /dev/null &

# Wait for ngrok to start and retrieve the public URL
sleep 5  # Wait for ngrok to initialize

if [ "$NGROK_URL" != "null" ]; then
    log "ngrok is running. Public URL: $NGROK_URL/whatsapp"
else
    log "Error: Could not retrieve ngrok URL. Make sure ngrok is running."
    exit 1
fi

# Output instructions for the user to use this URL with Twilio
log "Use the following URL in your Twilio configuration to receive WhatsApp messages:"
log "$NGROK_URL/whatsapp"

# Wait for the user to exit
wait
