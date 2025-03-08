import openai
from typing import List, Dict
import os
from groq import Groq


class LLMService:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        
    def get_response(self, messages: List[Dict[str, str]], max_tokens: int = 150) -> str:
        """
        Get a response from the LLM based on the conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            str: The LLM's response
        """
        try:
            response = self.client.chat.completions.create(
                model="qwen-2.5-32b",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM service: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment. Could you please repeat that?"
            
    def format_conversation_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format the conversation history for the LLM.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List[Dict[str, str]]: Formatted conversation history
        """
        system_prompt = {
            "role": "system",
            "content": """You are a helpful and professional call center AI assistant. 
            Your responses should be clear, concise, and focused on helping the caller.
            Always maintain a professional and friendly tone."""
        }
        
        formatted_messages = [system_prompt]
        formatted_messages.extend(messages)
        return formatted_messages 