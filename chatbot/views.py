from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ChatMessage
from .chatbot import Chatbot

# Initialize the chatbot
chatbot = Chatbot()

def home(request):
    """Render the home page with the chat interface"""
    # Get all previous messages
    messages = ChatMessage.objects.all()
    return render(request, 'chatbot/home.html', {'messages': messages})

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Handle chat requests"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Save user message
        ChatMessage.objects.create(message=user_message, is_user=True)
        
        # Get response from the bot
        response = chatbot.get_response(user_message)
        
        # Save bot response
        ChatMessage.objects.create(message=response, is_user=False)
        
        return JsonResponse({
            'response': response
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def clear_chat(request):
    try:
        chatbot.clear_history()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
