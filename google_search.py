from dotenv import load_dotenv
import google.generativeai as genai
import os
import requests
import json
from datetime import datetime

load_dotenv()
# Access environment variables
api_key = os.getenv("GOOGLE_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

genai.configure(api_key=api_key)

class SimpleSearchAgent:
    def __init__(self, model, serper_api_key):
        self.model = model
        self.serper_api_key = serper_api_key
    
    def search(self, query):
        """Search using Serper API and summarize results with the LLM"""
        try:
            # Get search results
            search_results = self._get_search_results(query)
            
            # Extract relevant information
            snippets = []
            for result in search_results.get('organic', []):
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                snippets.append(f"Title: {title}\nSnippet: {snippet}\nURL: {link}\n")
            
            # If there are top stories, include them
            for result in search_results.get('news', []):
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                date = result.get('date', '')
                snippets.append(f"News Title: {title}\nDate: {date}\nSnippet: {snippet}\nURL: {link}\n")
            
            # Combine all snippets
            all_snippets = "\n\n".join(snippets)
            
            # Create prompt for the LLM to summarize the results
            current_date = datetime.now().strftime("%Y-%m-%d")
            prompt = f"""
            Today is {current_date}. I need a comprehensive summary of the latest information on the following topic:
            
            Query: {query}
            
            Here are search results to help you provide accurate information:
            
            {all_snippets}
            
            Please analyze these search results and provide:
            1. A comprehensive summary of the current situation
            2. Key points from the most reliable sources
            3. Include relevant dates and facts
            
            Focus on factual information and avoid speculation. If there's conflicting information, acknowledge it.
            """
            
            # Create a chat session with appropriate instructions
            chat = self.model.start_chat()
            
            # Generate summary using the LLM
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Error in search: {e}")
            return f"I encountered an error while searching for information: {str(e)}"
    
    def _get_search_results(self, query):
        """Get search results using Serper API"""
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": query,
                "gl": "us",
                "hl": "en",
                "num": 10
            })
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making search request: {e}")
            # Return an empty result structure in case of errors
            return {"organic": [], "news": []}

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

# Create a singleton search agent
_search_agent = None

def get_search_agent():
    """Get or create the search agent singleton"""
    global _search_agent
    if _search_agent is None:
        _search_agent = SimpleSearchAgent(model, serper_api_key)
    return _search_agent

def search_web(query):
    """Main function to search the web and get AI summary
    
    Args:
        query (str): The search query
        
    Returns:
        str: AI-generated summary of search results
    """
    agent = get_search_agent()
    return agent.search(query)