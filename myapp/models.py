

from django.db import models
from django.contrib.auth.models import User

class Doc(models.Model):
    Title = models.CharField(max_length=255, unique=True)
    discription = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='docs')
    AI_description = models.TextField(blank=True, null=True)
    AI_questions = models.TextField(blank=True, null=True) # Field to store AI-generated questions
    Text = models.TextField(blank=True, null=True)  # Field to store extracted text from PDF



    def __str__(self):
        return self.Title




class ChatMessage(models.Model):
    user_message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_docs')
    assistant_response = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.user_message[:50]  # Return first 50 characters of the message
