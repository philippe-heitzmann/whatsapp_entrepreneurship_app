from flask import Flask, request, session
from flask_session import Session
import logging
import os
from twilio.twiml.messaging_response import MessagingResponse
from typing import Dict, List
from utils import query_chatgpt_assistant, create_prompt_mentor_bot, split_message

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
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')

    logging.info(f"Received message from {from_number}: {incoming_msg}")

    # Retrieve or initialize conversation history and thread ID
    conversation_history = session.get('conversation_history', [])
    thread_id = session.get('thread_id')  # Check if a thread ID exists

    resp = MessagingResponse()
    
    if incoming_msg:
        logging.info("Attempting to create a response to the received message...")
        
        # Generate a response, create a new thread if none exists
        response_text, updated_conversation_history, thread_id = handle_message(
            incoming_msg, conversation_history, thread_id
        )
        logging.info(f"Response created: {response_text} of length {len(response_text)}")

        split_responses = split_message(response_text)
        for split_response in split_responses:
            msg = resp.message()
            msg.body(split_response)

        # Update session with conversation history and thread ID
        session['conversation_history'] = updated_conversation_history
        session['thread_id'] = thread_id
    else:
        logging.info("No valid message received. Sending default error response.")
        msg = resp.message("I couldn't understand that. Please try again.")
    
    return str(resp)


def handle_message(message: str, conversation_history: List[Dict[str, str]], thread_id: str):
    """
    Process the incoming message, query ChatGPT, and return a response along with updated conversation history.

    Args:
        client (OpenAIClient): The OpenAI client instance.
        message (str): The user's message text.
        conversation_history (List[Dict[str, str]]): List of previous exchanges.
        thread_id (str): Existing thread ID; None if it's a new conversation.

    Returns:
        tuple: (response text, updated conversation history, thread ID)
    """
    # Add user message to conversation history
    conversation_history.append({'role': 'user', 'content': message})

    # Create prompt for the assistant
    prompt = create_prompt_mentor_bot(conversation_history, message)
    logging.info(f"Generated prompt for ChatGPT")

    # Query the assistant
    response, thread_id = query_chatgpt_assistant(prompt, thread_id=thread_id)
    logging.info(f"ChatGPT response: {response}")

    # Add assistant response to history
    conversation_history.append({'role': 'assistant', 'content': response})

    return response, conversation_history, thread_id



if __name__ == '__main__':
    # Run the Flask app in debug mode for development
    app.run(debug=True, host="0.0.0.0", port=5006)
