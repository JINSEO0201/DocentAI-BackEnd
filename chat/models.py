from django.db import models
from user.models import User

class Chat(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_user')
  artwork_id = models.IntegerField(null=False)
  exhibition_id = models.IntegerField(null=False)
  chat_history = models.JSONField(null=True)
  