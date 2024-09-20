from flask import Flask, request, session
import logging
import os
from twilio.twiml.messaging_response import MessagingResponse
from typing import Dict, List
from utils import query_chatgpt, create_prompt_business_plan, create_prompt_generate_business_plan, generate_business_plan_document, upload_file_to_gcs

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Flask app configuration
app = Flask(__name__)
app.secret_key = 'secret_key1'  # Replace with a strong secret key
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
    msg = resp.message()

    # Check if the message contains any content
    if incoming_msg:
        logging.info("Attempting to create a response to the received message...")
        # Process the message and generate a response
        response_text = handle_message(incoming_msg, conversation_history)
        logging.info(f"Response created: {response_text}")
        msg.body(response_text)

        # Save the updated conversation history in the session
        session['conversation_history'] = conversation_history
    else:
        logging.info("No valid message received. Sending default error response.")
        msg.body("I couldn't understand that. Please try again.")
    
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
    prompt = create_prompt_business_plan(conversation_history)
    logging.info(f"Generated prompt for ChatGPT: {prompt}")

    # Query ChatGPT with the prompt
    response = query_chatgpt(prompt)
    logging.info(f"ChatGPT response: {response}")

    # Add ChatGPT's response to conversation history
    conversation_history.append({'role': 'assistant', 'content': response})

    # If ChatGPT determines enough information is gathered
    if "3have_info3" in response:
        # Generate full business plan
        business_plan_prompt = create_prompt_generate_business_plan(conversation_history)
        full_business_plan = query_chatgpt(business_plan_prompt)
        logging.info(f"Generated business plan: {full_business_plan}")

        # Generate a document and upload it to GCS
        document_file_path = generate_business_plan_document(full_business_plan, file_format='docx')
        blob_name = os.path.basename(document_file_path)  # Use the local file name for GCS blob
        public_url = upload_file_to_gcs(document_file_path, GCS_BUCKET_NAME, blob_name)

        # Check if the document was uploaded successfully
        if public_url:
            return f"Thank you for providing all the necessary information. Your business plan has been generated. You can download it here: {public_url}"
        else:
            return "There was an issue generating your business plan. Please try again later."

    # Otherwise, return the next question from ChatGPT
    return response

if __name__ == '__main__':
    # Run the Flask app in debug mode for development
    app.run(debug=True, host="0.0.0.0", port=5005)
