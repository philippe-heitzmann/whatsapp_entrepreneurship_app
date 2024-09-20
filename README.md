# Business Plan Generator Chatbot App

This repository creates an application allowing a user to interact with a chatbot via WhatsApp, which asks questions about their business model to generate a sample business plan. The chatbot collects responses and generates a Google Doc with the structured business plan based on user inputs.

## Prerequisites

- Docker must be installed on your machine. You can download it from [here](https://www.docker.com/get-started).
- A valid `credentials.json` file must be present in the root directory of this project. This file should contain Google API credentials for authenticating the Google Docs and Drive APIs.
- A Twilio account for WhatsApp messaging.

## Setup

### 1. Google Cloud Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Cloud Storage API** and **Google Docs API**.
3. Create a **Service Account** and download the credentials as `gcs_credentials.json`.
4. Move the `gcs_credentials.json` file to the root of this project directory.

### 2. Twilio Setup

1. Sign up for a Twilio account at [Twilio Signup](https://www.twilio.com/try-twilio).
2. Navigate to the [Twilio Console](https://www.twilio.com/console) and create a **Twilio WhatsApp Sandbox**.
3. You'll be given a WhatsApp number and a sandbox keyword to activate WhatsApp messaging.
4. Set the webhook URL to the `ngrok` link you'll generate in the next section. The link should point to `/whatsapp` (e.g., `https://[ngrok_link]/whatsapp`).

### 3. Running the Bot

1. Open a terminal.
2. Navigate to the `scripts` folder:
   ```bash
   cd ./src/scripts
   sh ./build_run.sh
3. This will build and run the Dockerfile on your localhost.
4. Once the app is running, it will be accessible via the generated ngrok link (displayed in your terminal).
5. Copy this link and update your Twilio Webhook in the WhatsApp Sandbox settings with the ngrok link followed by /whatsapp (e.g., https://[ngrok_link]/whatsapp).

### 4. Testing the Bot
1.  Use your phone to send a WhatsApp message to the Twilio Sandbox number.
2.  Send the activation keyword provided by Twilio to start interacting with the bot.
3.  The bot will start asking questions about your business and generate a business plan in a Google Doc once all necessary information is collected.
4.  Once the document is generated, a download link to the business plan will be sent back to your WhatsApp conversation.

## How the Bot Functions (High-Level Overview)
1.  The bot uses Twilio to receive and send WhatsApp messages.
2.  Each response is processed using OpenAI's GPT model to generate the next question or business plan text.
3.  Once all the necessary information is collected, a Google Doc is generated, stored in Google Cloud, and a public link is sent to the user.

## Demo
Check out a demo of the bot in action by clicking [here](https://youtu.be/628mz4JronE).