# secure_file_transfer\file_transfer\models.py
from django.db import models
from django.contrib.auth.models import User

class FileTransfer(models.Model):
    """
    Model to track file transfer history
    """
    TRANSFER_TYPES = [
        ('upload', 'Upload'),
        ('download', 'Download'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    transfer_type = models.CharField(max_length=10, choices=TRANSFER_TYPES)
    file = models.FileField(upload_to='encrypted_files/')
    salt = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.transfer_type}"