from django.db import models
from django.contrib.auth.models import User


class ContactMessage(models.Model):
    """
    Model to store user messages to the admin team.
    Includes fields for future admin responses and email notifications.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contact_messages',
        help_text='The user who sent this message'
    )
    subject = models.CharField(
        max_length=200,
        help_text='Subject of the message'
    )
    message = models.TextField(
        help_text='Content of the message'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the message'
    )
    admin_response = models.TextField(
        blank=True,
        null=True,
        help_text='Admin response to the message'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the message was created'
    )
    responded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the admin responded'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.subject} - {self.user.email} ({self.status})"
