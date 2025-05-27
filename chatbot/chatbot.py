import sys
import os

# Add the AI directory to the Python path
ai_dir = os.path.join(os.path.dirname(__file__), '..', 'AI')
sys.path.append(ai_dir)

# Change working directory to AI directory to ensure file paths are correct
os.chdir(ai_dir)

from chadbot_sigma_v1 import NDWDocBot

class Chatbot:
    def __init__(self):
        self.bot = NDWDocBot()
    
    def get_response(self, message):
        """Get a response from the chatbot"""
        return self.bot.get_response(message)
    
    def clear_history(self):
        """Clear the chat history"""
        self.bot.clear_history() 