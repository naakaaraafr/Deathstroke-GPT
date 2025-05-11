# Deathstroke GPT

**Deathstroke GPT** is a Streamlit-based AI assistant that combines multiple AI-powered features to help users with tasks such as:

* 💬 **General Chat**: Ask any question and get intelligent responses.
* 📧 **Email Drafting**: Write and send emails via Gmail SMTP.
* 🔍 **Web Search**: Search the web and get AI-generated summaries.
* 🎨 **Image Generation**: Create custom AI-generated images using Hugging Face or placeholders.
* 📸 **Image Analysis**: Upload images and receive analytical insights.

---

## 🚀 Features

* **Multi-Modal Interaction**: Text chat, email drafting, web search, image generation, and image analysis.
* **Built with Streamlit**: Quick deployment and an intuitive UI.
* **Google Gemini API**: Uses Google Generative AI for chat, email subject/body, and web search summarization.
* **Hugging Face Stable Diffusion XL**: (Optional) High-quality image generation when `HUGGINGFACE_API_TOKEN` is set.
* **Configurable Environment**: Securely manage API keys and secrets via a `.env` file.

---

## 🛠️ Prerequisites

* Python 3.8+
* Pip or Poetry for dependency management
* A Gmail account with an app-specific password for email sending.
* API keys:

  * `GOOGLE_API_KEY` for Google Gemini
  * `SERPER_API_KEY` for Serper search API
  * (Optional) `HUGGINGFACE_API_TOKEN` for Stable Diffusion

---

## ⚡ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/deathstroke-gpt.git
   cd deathstroke-gpt
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create your `.env` file** in the project root:

   ```text
   GOOGLE_API_KEY=your_google_api_key
   SERPER_API_KEY=your_serper_api_key
   EMAIL_SENDER=your_email_address
   EMAIL_PASSWORD=your_email_app_password
   HUGGINGFACE_API_TOKEN=your_huggingface_token  # optional for image gen
   ```

---

## 📁 Project Structure

```text
├── .env                  # Environment variables (ignored by git)
├── email_sender.py       # Module for drafting and sending emails
├── google_search.py      # Web search agent using Serper and Gemini
├── image_gen.py          # AI image generation and placeholder logic
├── reg_query_cb.py       # General query callback for chat and image analysis
├── main.py               # Streamlit application entrypoint
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 📝 Usage

**Run the app locally**:

```bash
streamlit run main.py
```

1. Open your browser at `http://localhost:8501`.
2. Use the sidebar to see available features and set up your Hugging Face token if needed.
3. Chat with Deathstroke GPT, draft emails, search the web, generate images, or upload photos for analysis.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or pull requests for feature requests, bug fixes, or improvements.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

*Built with ❤️ and AI-powered by Google Gemini and Hugging Face.*
