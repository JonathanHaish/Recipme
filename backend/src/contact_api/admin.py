from django.contrib import admin
from django.utils import timezone
from .models import ContactMessage
from mysite.email_templates import send_contact_response_email


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing contact messages.
    Staff users can view messages and respond to them.
    When a response is saved, an email is sent to the user.
    """
    
    list_display = ('subject', 'user_email', 'status', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message', 'user__email', 'admin_response')
    readonly_fields = ('user', 'subject', 'message', 'created_at', 'responded_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Message Details', {
            'fields': ('user', 'subject', 'message', 'created_at'),
            'description': 'Original message from the user (read-only)'
        }),
        ('Admin Response', {
            'fields': ('status', 'admin_response', 'responded_at'),
            'description': 'Fill in your response and set status to "Responded" to send an email to the user'
        }),
    )
    
    def user_email(self, obj):
        """Display user's email in the list view"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def save_model(self, request, obj, form, change):
        """
        Override save to send email when admin responds.
        Email is sent when:
        - status is changed to 'responded'
        - admin_response is not empty
        """
        # Check if this is a response being saved
        is_responding = (
            obj.status == 'responded' and 
            obj.admin_response and 
            obj.admin_response.strip()
        )
        
        # Check if this is a new response (not already responded)
        was_pending = False
        if change:  # If this is an update (not a new object)
            old_obj = ContactMessage.objects.get(pk=obj.pk)
            was_pending = old_obj.status == 'pending'
        
        # Set responded_at timestamp if responding
        if is_responding and was_pending:
            obj.responded_at = timezone.now()
        
        # Save the model first
        super().save_model(request, obj, form, change)
        
        # Send email if this is a new response
        if is_responding and was_pending:
            self._send_response_email(obj)
    
    def _send_response_email(self, obj):
        """Send branded email notification to user with admin's response"""
        send_contact_response_email(
            to_email=obj.user.email,
            original_subject=obj.subject,
            original_message=obj.message,
            admin_response=obj.admin_response
        )
    
    def has_add_permission(self, request):
        """Disable adding messages through admin - users submit via the frontend"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete messages"""
        return request.user.is_superuser
