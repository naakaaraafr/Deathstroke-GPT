import streamlit as st
import os
from dotenv import load_dotenv
from email_sender import generate_email_content, send_email
from google_search import search_web
from image_gen import generate_image
from reg_query_cb import generate_response
import re
import io

load_dotenv()

st.set_page_config(
    page_title="Deathstroke GPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    .main-header {
        font-size: 42px;
        font-weight: bold;
        background: linear-gradient(90deg, #9146FF, #764BA2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
        text-align: center;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .chat-message.assistant {
        background-color: #1A1A2E;
        border-left: 5px solid #9146FF;
        color: #E0E0E0;
    }
    div[data-testid="stFileUploader"] {
        padding: 1rem;
        border: 1px dashed #9146FF;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        background-color: #1E1E1E;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #2D2D2D;
        color: #E0E0E0;
        border: 1px solid #3D3D3D;
    }
    .st-emotion-cache-16idsys p, .st-emotion-cache-16idsys li {
        color: #E0E0E0;
    }
    div[data-testid="stSidebarUserContent"] label, .stTextInput label, .stTextArea label {
        color: #B0B0B0;
    }
    .st-be, .st-cj, .st-cx, .st-da {
        color: #E0E0E0;
    }
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    .stButton button {
        background-color: #9146FF;
        color: white;
    }
    div[data-testid="stChatInput"] {
        background-color: #2D2D2D;
        border-radius: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        color: #888;
    }
    .info-box {
        padding: 10px;
        background-color: rgba(145, 70, 255, 0.1);
        border-left: 3px solid #9146FF;
        margin-bottom: 10px;
    }
    </style>
    <div class="main-header">Deathstroke GPT</div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🤖 Deathstroke GPT Features")
    st.markdown("- 💬 **General Chat** - Ask any question")
    st.markdown("- 📧 **Email Drafting** - Write and send emails")
    st.markdown("- 🔍 **Web Search** - Find information online")
    st.markdown("- 🎨 **Image Generation** - Create custom images")
    st.markdown("- 📸 **Image Analysis** - Upload images for analysis")
    st.divider()
    
    # Check if Hugging Face API token is set
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not hf_token:
        st.warning("⚠️ Hugging Face API token not set. Image generation will use placeholders.")
        with st.expander("How to set up API token"):
            st.markdown("""
            1. Create an account on [Hugging Face](https://huggingface.co/)
            2. Get your API token from [Settings > API Tokens](https://huggingface.co/settings/tokens)
            3. Create a `.env` file in your project root with: `HUGGINGFACE_API_TOKEN=your_token_here`
            4. Restart the application
            """)
    
    st.markdown("### 💡 Usage Tips")
    st.markdown("**For emails**: Try 'Write an email to the team about project updates'")
    st.markdown("**For search**: Try 'Search for latest AI developments'")
    st.markdown("**For images**: Try 'Generate an image of a mountain sunset'")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'email_body' not in st.session_state:
    st.session_state.email_body = None
if 'email_recipient' not in st.session_state:
    st.session_state.email_recipient = None
if 'email_subject' not in st.session_state:
    st.session_state.email_subject = None

def identify_query_type(query):
    query_lower = query.lower()
    email_patterns = [
        r'(send|write|draft|compose|prepare).*(email|mail|message|letter)',
        r'email to .* about',
        r'write .* an email'
    ]
    search_patterns = [
        r'(search|find|look up|research)',
        r'(what is|who is|where is|when is|why is|how is)',
        r'tell me about',
        r'(latest|news|information) (on|about)',
        r'can you find',
        r'look for'
    ]
    image_patterns = [
        r'(generate|create|draw|make|design|show|give me).*(image|picture|photo|artwork|illustration|drawing|visual)',
        r'visualize',
        r'(show|create) .* (picture|visualization)'
    ]
    for pattern in email_patterns:
        if re.search(pattern, query_lower):
            return "email"
    for pattern in search_patterns:
        if re.search(pattern, query_lower):
            return "search"
    for pattern in image_patterns:
        if re.search(pattern, query_lower):
            return "image"
    return "general"

col1, col2 = st.columns([7, 3])

with col2:
    st.markdown("### 📸 Upload Image")
    uploaded_file = st.file_uploader("Upload an image for analysis", type=["png", "jpg", "jpeg"],
                                    help="Upload an image to ask questions about it")
    if uploaded_file:
        st.session_state.uploaded_image = uploaded_file
        st.image(uploaded_file, width=250, caption="Uploaded image")
        st.success("✅ Image uploaded successfully!")

with col1:
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    <div>👤 <b>You:</b> {message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if "image_data" in message:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div>🤖 <b>Assistant:</b> {message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.image(message["image_data"], caption="Generated Image", use_container_width=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div>🤖 <b>Assistant:</b> {message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

query = st.chat_input("Ask me anything, I will try to answer as best as I can...")

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})
    with chat_container:
        st.markdown(f"""
        <div class="chat-message user">
            <div>👤 <b>You:</b> {query}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.spinner("🤖 Thinking..."):
        query_type = identify_query_type(query)
        try:
            if query_type == "email":
                with st.spinner("Generating email draft..."):
                    email_body, email_recipient, subject = generate_email_content(query)
                    st.session_state.email_body = email_body
                    st.session_state.email_recipient = email_recipient
                    st.session_state.email_subject = subject
                
                # Format the response content
                response_content = f"**Draft Email**\n\n**To:** {email_recipient}\n**Subject:** {subject}\n\n{email_body}"
                
                # Display the email draft
                with chat_container:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div>🤖 <b>Assistant:</b> {response_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create columns for the send button and status message
                    col1, col2 = st.columns([1, 5])
                    
                    # Place the send button in the first column
                    with col1:
                        send_pressed = st.button("✉️ Send Email", key="send_email_btn", type="primary")
                    
                    # Handle sending the email if the button is pressed
                    if send_pressed:
                        status_placeholder = col2.empty()
                        with status_placeholder.container():
                            with st.spinner("Sending email..."):
                                try:
                                    # Log email details before sending
                                    st.session_state.email_details = {
                                        "body": st.session_state.email_body[:100] + "...",
                                        "recipient": st.session_state.email_recipient,
                                        "subject": st.session_state.email_subject
                                    }
                                    
                                    # Try to send the email
                                    success = send_email(
                                        st.session_state.email_body,
                                        st.session_state.email_recipient,
                                        st.session_state.email_subject
                                    )
                                    
                                    # Display appropriate message based on success
                                    if success:
                                        st.success("Email sent successfully! ✅")
                                    else:
                                        st.error("Failed to send email. Check the logs for more details. ❌")
                                        st.info("Make sure your Gmail app password is valid and less secure apps are enabled.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    st.info("Try using the test script to debug email sending outside Streamlit.")
                
                # Add the assistant's response to the chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response_content})
            
            elif query_type == "search":
                response_content = search_web(query)
                with chat_container:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div>🤖 <b>Assistant:</b> {response_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": response_content})
            
            elif query_type == "image":
                with chat_container:
                    with st.status("Generating image...", expanded=True) as status:
                        try:
                            # Check if HF token is set
                            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
                            if not hf_token:
                                st.info("⚠️ Note: Using placeholder images because Hugging Face API token is not set.")
                            
                            result = generate_image(query)
                            if result["success"]:
                                response_text = f"Here's the image I generated based on: '{query}'"
                                status.update(label="Image generated successfully! ✨", state="complete", expanded=False)
                                st.markdown(f"""
                                <div class="chat-message assistant">
                                    <div>🤖 <b>Assistant:</b> {response_text}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.image(result["image_bytes"], caption="Generated Image", use_container_width=True)
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": response_text,
                                    "image_data": result["image_bytes"]
                                })
                            else:
                                status.update(label="Using placeholder image", state="complete", expanded=False)
                                error_message = f"I've created a placeholder image based on your prompt. To generate real AI images, please set up your Hugging Face API token."
                                
                                # Add helpful information if the error is about the API token
                                if "API token not found" in result["error_message"] or "API usage disabled" in result["error_message"]:
                                    st.markdown("""
                                    <div class="info-box">
                                        <p><strong>💡 To enable AI image generation:</strong></p>
                                        <ol>
                                        <li>Create an account on <a href="https://huggingface.co/" target="_blank">Hugging Face</a></li>
                                        <li>Get your API token from <a href="https://huggingface.co/settings/tokens" target="_blank">Settings > API Tokens</a></li>
                                        <li>Create a <code>.env</code> file in your project root with:<br/><code>HUGGINGFACE_API_TOKEN=your_token_here</code></li>
                                        <li>Restart the application</li>
                                        </ol>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.warning(f"Note: {result['error_message']}")
                                
                                st.markdown(f"""
                                <div class="chat-message assistant">
                                    <div>🤖 <b>Assistant:</b> {error_message}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.image(result["image_bytes"], caption="Placeholder Image", use_container_width=True)
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": error_message,
                                    "image_data": result["image_bytes"]
                                })
                        except Exception as e:
                            status.update(label="Image generation failed", state="error", expanded=False)
                            error_message = f"There was an unexpected error: {str(e)}"
                            st.error(error_message)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_message})
            
            else:
                if st.session_state.uploaded_image:
                    response_content = generate_response(query, st.session_state.uploaded_image)
                else:
                    response_content = generate_response(query)
                with chat_container:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div>🤖 <b>Assistant:</b> {response_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": response_content})
        
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            with chat_container:
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div>🤖 <b>Assistant:</b> ⚠️ {error_message}</div>
                </div>
                """, unsafe_allow_html=True)
            st.session_state.chat_history.append({"role": "assistant", "content": error_message})

st.markdown("""
<div class="footer">
    <p>© 2025 Deathstroke GPT - Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)