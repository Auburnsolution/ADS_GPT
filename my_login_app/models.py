from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    email=models.EmailField(blank=True)
    profile_pic=models.ImageField(upload_to='profile_pics',blank=True)
    portfolio=models.URLField(blank=True)

    def __str__(self):
        return self.user.username
    


class ChatHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    response = models.TextField()
    def __str__(self):
        # Customize this to display the information you find most useful
        return f"Chat on {self.timestamp} by {self.user.username}"


