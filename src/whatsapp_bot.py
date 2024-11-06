from flask import Flask, request, session
from flask_session import Session
import logging
import os
from twilio.twiml.messaging_response import MessagingResponse
from typing import Dict, List
from utils import query_chatgpt, create_prompt_mentor_bot, split_message

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Flask app configuration
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'secret_key1'  # Replace with a strong secret key
Session(app)
GCS_BUCKET_NAME = "hbs_foundry_demo2"

# Flag to track if the function has already run
setup_done = False

@app.before_request
def setup_once():
    global setup_done
    if not setup_done:
        # Run your one-time setup code here
        session.clear()  # Clear session when the server starts
        setup_done = True  # Ensure this block runs only once
        logging.info("Initial setup done, session cleared.")

# Usage in the whatsapp_bot function
@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot() -> str:
    """
    Endpoint for receiving incoming WhatsApp messages.
    This method is triggered when a POST request is sent to the /whatsapp endpoint.
    
    The incoming WhatsApp message is processed, and an appropriate response is generated
    and sent back using Twilio's MessagingResponse API.
    
    Returns:
        str: The TwiML XML response to be sent to the Twilio API.
    """
    # Extract the incoming message and sender's number
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')

    # Log the incoming message and the sender
    logging.info(f"Received message from {from_number}: {incoming_msg}")

    # Retrieve or initialize the session for conversation history
    if 'conversation_history' not in session:
        session['conversation_history'] = []  # Initialize if it's the first message from the user

    conversation_history = session['conversation_history']  # Fetch conversation history

    # Initialize Twilio response object
    resp = MessagingResponse()
    
    # Check if the message contains any content
    if incoming_msg:
        logging.info("Attempting to create a response to the received message...")
        # Process the message and generate a response
        response_text, updated_conversation_history = handle_message(incoming_msg, conversation_history)
        logging.info(f"Response created: {response_text} of length {len(response_text)}")

        # Split the response text and send each part in a separate message
        split_responses = split_message(response_text)
        for split_response in split_responses:
            msg = resp.message()  # Create a new message for each split part
            msg.body(split_response)

        # Save the updated conversation history in the session
        session['conversation_history'] = updated_conversation_history
    else:
        logging.info("No valid message received. Sending default error response.")
        msg = resp.message("I couldn't understand that. Please try again.")
    
    # Return TwiML XML (Twilio format)
    return str(resp)


def handle_message(message: str, conversation_history: List[Dict[str, str]]) -> str:
    """
    Process the incoming WhatsApp message and return an appropriate response. 
    It checks the user's previous responses and uses ChatGPT to ask the next relevant question
    for the business plan.

    Args:
        message (str): The message text sent by the user.
        conversation_history (List[Dict[str, str]]): List of previous exchanges (user and assistant).

    Returns:
        str: The next question to ask the user or confirmation that enough information is available.
    """
    # Add the new message to conversation history
    conversation_history.append({'role': 'user', 'content': message})

    # Create the next prompt for ChatGPT to determine the next question or response
    prompt = create_prompt_mentor_bot(conversation_history, message)
    logging.info(f"Generated prompt for ChatGPT")
    # logging.info(f"Generated prompt for ChatGPT: {prompt}")

    # Query ChatGPT with the prompt
    response = query_chatgpt(prompt)
    logging.info(f"ChatGPT response: {response}")

    # Add ChatGPT's response to conversation history
    conversation_history.append({'role': 'assistant', 'content': response})

    # Otherwise, return the next question from ChatGPT
    return response, conversation_history

if __name__ == '__main__':
    # Run the Flask app in debug mode for development
    app.run(debug=True, host="0.0.0.0", port=5006)
