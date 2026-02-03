"""
LLM interface for OpenAI
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    USE_STREAMLIT_SECRETS = True
except ImportError:
    USE_STREAMLIT_SECRETS = False

load_dotenv()

class LLMClient:
    def __init__(self):
        # Try Streamlit secrets first (for cloud), then fall back to .env (for local)
        if USE_STREAMLIT_SECRETS and hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
        else:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file or Streamlit secrets")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Using GPT-4o (latest, cheaper than GPT-4)
    
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """
        Generate a response from OpenAI
        
        Args:
            system_prompt: Instructions for the AI
            user_prompt: The actual query
            temperature: Creativity level (0.0 = focused, 1.0 = creative)
        
        Returns:
            AI response as string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")