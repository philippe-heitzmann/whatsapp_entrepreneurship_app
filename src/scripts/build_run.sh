#!/bin/bash

# Set the working directory to the folder where the script is located
SCRIPT_DIR=$(dirname "$0")
ROOT_DIR=$(realpath "$SCRIPT_DIR/../../")

# Define the container name and image
IMAGE_NAME="whatsapp-business-plan-bot"

# Logging function for better readability
log() {
    echo "[INFO] $1"
}

# Check if the credentials.json file exists
# if [ ! -f "$ROOT_DIR/credentials.json" ]; then
#     log "Error: credentials.json not found in the root directory ($ROOT_DIR)."
#     exit 1
# fi

# Build the Docker image
log "Building Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME "$ROOT_DIR"
if [ $? -eq 0 ]; then
    log "Docker image built successfully."
else
    log "Error building Docker image."
    exit 1
fi

# Run the Docker container with credentials.json mounted and expose port 5000
log "Running Docker container from image: $IMAGE_NAME..."
# -v "$ROOT_DIR/credentials.json:/app/credentials.json"
docker run -d --env-file=./env/app.env -p 5005:5005 $IMAGE_NAME
if [ $? -eq 0 ]; then
    log "Docker container is running."
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
log "Starting ngrok to expose port 5005..."
ngrok http 5005 > /dev/null &

# Wait for ngrok to start and retrieve the public URL
sleep 5  # Wait for ngrok to initialize

# Get the public URL from ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ "$NGROK_URL" != "null" ]; then
    log "ngrok is running. Public URL: $NGROK_URL"
else
    log "Error: Could not retrieve ngrok URL. Make sure ngrok is running."
    exit 1
fi

# Output instructions for the user to use this URL with Twilio
log "Use the following URL in your Twilio configuration to receive WhatsApp messages:"
log "$NGROK_URL/whatsapp"

# Wait for the user to exit
wait
