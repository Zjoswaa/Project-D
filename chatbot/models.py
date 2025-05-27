from django.db import models

# Create your models here.

class ChatMessage(models.Model):
    message = models.TextField()
    is_user = models.BooleanField(default=True)  # True for user messages, False for bot responses
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
