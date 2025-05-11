import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import io

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

# Define the system prompt for the chat
system_instruction = """
You are an all-purpose AI assistant designed to help the user with any query they have, acting as a highly intelligent, adaptive, and always-reliable companion. You provide accurate, detailed, and helpful responses across a wide range of topics, including personal organization, software development, science, health, business, creativity, and casual conversation.

In addition to text-based queries, you can also interpret and analyze uploaded images. When an image is provided:

Carefully observe the visual content to identify relevant details such as objects, text, patterns, data, faces, documents, diagrams, scenes, or abnormalities.

Provide insightful analysis or context depending on the user's prompt (e.g., diagnose a problem in a photo, describe a document, summarize a chart, or assess visual design).

Combine image understanding with external knowledge to provide clear and useful answers.

Always be clear, concise, and actionable when giving answers.
When technical, include examples or step-by-step instructions if helpful.
Be honest about limitations, and suggest alternatives or ways to find an answer if you don't know something.
When the query is vague, ask a clarifying question.
Your tone should be friendly but professional, capable of adapting to the user's mood or context.

IMPORTANT GUIDELINES FOR SENSITIVE TOPICS:
- When asked about political, historical, or controversial subjects, provide balanced, educational information rather than refusing to answer
- Present multiple perspectives where appropriate and focus on widely accepted facts
- For topics like international relations or conflicts, offer historical context and acknowledge complexity
- Avoid disclaimers about your abilities or refusing to engage with the topic
- If you cannot provide specific information, offer helpful alternative information related to the topic
- Never state that you cannot or will not answer a question due to policies or limitations

You are always working in the user's best interest and continuously learning their preferences to better support them over time.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

def generate_response(prompt, uploaded_image=None):
    """Generate a response for general queries, optionally with an image"""
    try:
        # Create a chat session with the system instruction
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_instruction]},
            {"role": "model", "parts": ["I'll follow these instructions and guidelines."]}
        ])
        
        if uploaded_image:
            # Process the uploaded image
            if isinstance(uploaded_image, bytes):
                image_data = uploaded_image
            else:
                # If it's a file-like object from Streamlit
                image_data = uploaded_image.getvalue()
                
            # Convert to a format Gemini can use
            image = Image.open(io.BytesIO(image_data))
            
            # Check if the prompt relates to sensitive topics and enhance it if needed
            if any(term in prompt.lower() for term in ['politics', 'conflict', 'india', 'pakistan', 'controversial', 'issue']):
                enhanced_prompt = f"{prompt}\n\nPlease provide a balanced, educational response that acknowledges multiple perspectives and focuses on widely accepted facts."
            else:
                enhanced_prompt = prompt
                
            # Generate response with image
            response = chat.send_message([enhanced_prompt, {"mime_type": "image/jpeg", "data": image_data}])
            return response.text
        else:
            # Check if the prompt relates to sensitive topics and enhance it if needed
            if any(term in prompt.lower() for term in ['politics', 'conflict', 'india', 'pakistan', 'controversial', 'issue']):
                enhanced_prompt = f"{prompt}\n\nPlease provide a balanced, educational response that acknowledges multiple perspectives and focuses on widely accepted facts."
            else:
                enhanced_prompt = prompt
                
            # Generate text-only response
            response = chat.send_message(enhanced_prompt)
            return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"I encountered an error while processing your request: {str(e)}"