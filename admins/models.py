# admins/models.py
from django.db import models
from django.contrib.auth.models import User

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username