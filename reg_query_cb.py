import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import io

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Model configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# General-purpose system instruction
system_instruction = """
You are a smart, helpful, and friendly AI assistant that helps users with everyday tasks and questions. 
You can answer casual queries, explain concepts, help with writing, summarize topics, provide productivity tips, analyze images, and even tell jokes.

If the user uploads an image:
- Observe carefully and describe or interpret the image based on the prompt.
- Be specific and helpful (e.g., analyze text in photos, explain diagrams, evaluate scenes or products).

When answering:
- Be concise, but clear and engaging.
- Offer step-by-step help where useful.
- For vague queries, politely ask for clarification.

Tone: approachable, supportive, knowledgeable.

For sensitive or complex topics:
- Offer balanced and fact-based explanations.
- Avoid taking sides or expressing opinions.
- If uncertain, explain what is known and suggest where more information can be found.
"""

# Initialize Gemini model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

def generate_response(prompt, uploaded_image=None):
    """Generates a conversational response to the user's prompt, with optional image analysis."""
    try:
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_instruction]},
            {"role": "model", "parts": ["Absolutely! I'm here to help. What's next?"]}
        ])

        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            return "❗ Please enter a valid question or task so I can help you."

        if uploaded_image:
            # Get image data
            image_data = uploaded_image if isinstance(uploaded_image, bytes) else uploaded_image.getvalue()
            Image.open(io.BytesIO(image_data))  # Validate image format
            response = chat.send_message([cleaned_prompt, {"mime_type": "image/jpeg", "data": image_data}])
        else:
            response = chat.send_message(cleaned_prompt)

        return response.text

    except Exception as e:
        print(f"Error generating response: {e}")
        return f"⚠️ Oops! Something went wrong: {str(e)}"
