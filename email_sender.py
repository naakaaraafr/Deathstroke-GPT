from email.message import EmailMessage
import ssl
import smtplib
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# Access environment variables
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

import re
import smtplib
from email.message import EmailMessage
import ssl

def generate_email_content(prompt):
    """Generate email body, recipient, and subject based on the user's prompt"""
    try:
        # Generate email recipient
        recipient_system_prompt = """You are an AI assistant that helps the user determine the email address of the recipient based on the context provided. The output must contain only a valid email address and nothing else. If the context is vague or lacks sufficient information to determine the email address, respond with "recipient@example.com" as a placeholder."""
        recipient_chat = model.start_chat(history=[
            {"role": "user", "parts": [recipient_system_prompt]},
            {"role": "model", "parts": ["I'll provide email addresses based on your guidelines."]}
        ])
        email_recipient_response = recipient_chat.send_message(prompt)
        email_recipient = email_recipient_response.text.strip()
        # Extract a valid email address using regex for robustness
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_recipient)
        if email_match:
            email_recipient = email_match.group(0)
        else:
            email_recipient = "recipient@example.com"
        
        # Generate email subject
        subject_system_prompt = """You are an AI assistant that generates clear, relevant, and appropriately toned subject lines for emails based on a description provided by the user.

            Your goal is to create a concise and compelling subject line that reflects the purpose, urgency, and tone of the email.

            Adapt the formality and style of the subject line to match the described audience (e.g., client, colleague, manager, vendor).

            Prioritize clarity and brevity. Ideally, keep subject lines under 10 words unless otherwise instructed.

            Use action-driven or context-specific phrases where appropriate (e.g., "Reminder:", "Request for", "Follow-up on").

            Avoid vague, overly generic, or misleading language.
            
            Important: If the user is requesting information on a sensitive topic like politics, conflicts, or controversial issues, respond with a neutral subject like "Information Request" rather than rejecting the request.

            Only output the subject line — do not include the body or greeting of the email and not even the word "subject:"."""
        subject_chat = model.start_chat(history=[
            {"role": "user", "parts": [subject_system_prompt]},
            {"role": "model", "parts": ["I'll create email subject lines according to these guidelines."]}
        ])
        subject_response = subject_chat.send_message(prompt)
        subject = subject_response.text.strip()
        
        # Generate email body
        body_system_prompt = """
            You are an AI email writer that generates well-structured, clear, and appropriately toned email bodies based on user input.

            When given a description of the email's purpose, recipient, key points, and tone, you will create only the body of the email (excluding the subject line).

            Structure the body logically, with a greeting, main content, and sign-off (unless the user specifies otherwise).

            Adapt the tone to the user's instructions (e.g., formal, friendly, apologetic, persuasive, professional, etc.).

            Be concise, clear, and direct, with no unnecessary repetition.

            Maintain professionalism, tact, and politeness, especially in sensitive situations.

            Avoid jargon unless the user requests it or the context requires it.
            
            IMPORTANT: For requests on potentially sensitive topics:
            - Instead of refusing to generate content, provide a balanced, educational response that acknowledges multiple perspectives
            - For political, historical, or controversial topics, focus on presenting widely accepted facts rather than opinions
            - Avoid disclaimers about your capabilities or limitations
            - If you truly cannot provide specific information, suggest alternative, helpful information the user might want instead
            
            For example, if asked about a sensitive geopolitical issue, provide historical context, acknowledge different perspectives exist, and focus on educational aspects rather than refusing the request entirely.
            """
        body_chat = model.start_chat(history=[
            {"role": "user", "parts": [body_system_prompt]},
            {"role": "model", "parts": ["I'll help write email bodies following these guidelines."]}
        ])
        enhanced_prompt = f"{prompt}\n\nPlease provide a balanced, educational response that acknowledges multiple perspectives and focuses on widely accepted facts."
        email_body_response = body_chat.send_message(enhanced_prompt)
        email_body = email_body_response.text
        
        return email_body, email_recipient, subject
    except Exception as e:
        print(f"Error generating email content: {e}")
        return "Failed to generate email content.", "recipient@example.com", "Error Generating Email"

def send_email(email_body, email_recipient, subject):
    """Send an email with the given body, recipient, and subject"""
    try:
        import smtplib
        from email.message import EmailMessage
        import ssl
        import os
        
        # Detailed logging for debugging
        print("=== Email Sending Debug Information ===")
        print(f"Recipient: {email_recipient}")
        print(f"Subject: {subject}")
        print(f"Body preview: {email_body[:100]}...")
        
        # Email configuration
        email_sender = "Your sender email"  
        email_password = "Your app password"  
        # Check if recipient is valid
        if not email_recipient or '@' not in email_recipient:
            print(f"Invalid recipient email: {email_recipient}")
            return False
            
        # Create email message
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_recipient
        em['Subject'] = subject
        em.set_content(email_body)
        
        # Create secure SSL context
        context = ssl.create_default_context()
        
        # Log connection attempt
        print(f"Attempting to connect to SMTP server: smtp.gmail.com:465")
        
        # Connect to the SMTP server and send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            # Log login attempt
            print(f"Attempting to login with sender: {email_sender}")
            
            # Login to the SMTP server
            smtp.login(email_sender, email_password)
            
            # Log send attempt
            print(f"Sending email from {email_sender} to {email_recipient}")
            
            # Send the email
            smtp.sendmail(email_sender, email_recipient, em.as_string())
            
        print("Email sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"AUTHENTICATION ERROR: {e}")
        print("This usually means your email or password is incorrect, or you need to enable less secure apps")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"RECIPIENT ERROR: {e}")
        print("The recipient email address was refused by the server")
        return False
        
    except smtplib.SMTPException as e:
        print(f"SMTP ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False