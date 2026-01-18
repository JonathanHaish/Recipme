"""
Email templates matching the Recipme frontend design.
Uses inline CSS for maximum email client compatibility.
"""

from django.core.mail import EmailMultiAlternatives
from django.conf import settings


# SVG Chef Hat icon (simplified for email compatibility)
CHEF_HAT_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 13.87A4 4 0 0 1 7.41 6a5.11 5.11 0 0 1 1.05-1.54 5 5 0 0 1 7.08 0A5.11 5.11 0 0 1 16.59 6 4 4 0 0 1 18 13.87V21H6Z"/>
    <line x1="6" y1="17" x2="18" y2="17"/>
</svg>
'''


def get_base_template(content: str, preview_text: str = "") -> str:
    """
    Base HTML email template matching Recipme design.
    
    Args:
        content: The main HTML content to insert
        preview_text: Text shown in email preview (before opening)
    
    Returns:
        Complete HTML email string
    """
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recipme</title>
    <!--[if mso]>
    <style type="text/css">
        table {{ border-collapse: collapse; }}
        .content {{ width: 600px !important; }}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f9fafb; font-family: Arial, Helvetica, sans-serif;">
    <!-- Preview text (hidden) -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        {preview_text}
    </div>
    
    <!-- Main container -->
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9fafb;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                
                <!-- Email card -->
                <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border: 2px solid #000000; border-radius: 8px;">
                    
                    <!-- Header with logo -->
                    <tr>
                        <td align="center" style="padding: 30px 40px 20px 40px; border-bottom: 2px solid #000000;">
                            <table role="presentation" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="color: #000000; vertical-align: middle; padding-right: 12px;">
                                        {CHEF_HAT_SVG}
                                    </td>
                                    <td style="vertical-align: middle;">
                                        <span style="font-size: 28px; font-weight: bold; color: #000000;">Recipme</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px 40px;">
                            {content}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; border-top: 1px solid #e5e7eb; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #6b7280;">
                                &copy; 2026 Recipme. All rights reserved.
                            </p>
                            <p style="margin: 8px 0 0 0; font-size: 12px; color: #6b7280;">
                                This email was sent by the Recipme team.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
'''


def get_button_html(text: str, url: str) -> str:
    """Generate a black button matching the frontend design."""
    return f'''
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin: 24px 0;">
        <tr>
            <td align="center" style="background-color: #000000; border-radius: 6px;">
                <a href="{url}" target="_blank" style="display: inline-block; padding: 12px 24px; font-size: 14px; font-weight: 600; color: #ffffff; text-decoration: none;">
                    {text}
                </a>
            </td>
        </tr>
    </table>
    '''


def send_branded_email(
    subject: str,
    to_email: str,
    html_content: str,
    plain_text: str,
    preview_text: str = ""
) -> bool:
    """
    Send an email with the Recipme branded template.
    
    Args:
        subject: Email subject
        to_email: Recipient email address
        html_content: HTML content for the email body
        plain_text: Plain text fallback
        preview_text: Preview text shown in email clients
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        html_email = get_base_template(html_content, preview_text)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.attach_alternative(html_email, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


# =============================================================================
# Pre-built email templates
# =============================================================================

def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """Send password reset email with branded template."""
    
    subject = "Password Reset Request - Recipme"
    preview_text = "Reset your Recipme password"
    
    html_content = f'''
        <h2 style="margin: 0 0 16px 0; font-size: 20px; font-weight: bold; color: #000000;">
            Password Reset Request
        </h2>
        <p style="margin: 0 0 16px 0; font-size: 14px; color: #374151; line-height: 1.6;">
            Hello,
        </p>
        <p style="margin: 0 0 16px 0; font-size: 14px; color: #374151; line-height: 1.6;">
            You requested to reset your password for your Recipme account. Click the button below to set a new password:
        </p>
        
        {get_button_html("Reset Password", reset_link)}
        
        <p style="margin: 0 0 16px 0; font-size: 14px; color: #374151; line-height: 1.6;">
            Or copy and paste this link into your browser:
        </p>
        <p style="margin: 0 0 16px 0; font-size: 12px; color: #6b7280; word-break: break-all;">
            {reset_link}
        </p>
        
        <div style="margin-top: 24px; padding: 16px; background-color: #f9fafb; border-radius: 6px; border: 1px solid #e5e7eb;">
            <p style="margin: 0; font-size: 12px; color: #6b7280;">
                <strong>Note:</strong> This link will expire in 24 hours. If you didn't request this password reset, you can safely ignore this email.
            </p>
        </div>
    '''
    
    plain_text = f"""
Password Reset Request - Recipme

Hello,

You requested to reset your password for your Recipme account.

Click here to reset your password:
{reset_link}

This link will expire in 24 hours.

If you didn't request this password reset, you can safely ignore this email.

Best regards,
The Recipme Team
"""
    
    return send_branded_email(subject, to_email, html_content, plain_text, preview_text)


def send_contact_response_email(
    to_email: str,
    original_subject: str,
    original_message: str,
    admin_response: str
) -> bool:
    """Send contact form response email with branded template."""
    
    subject = f"Re: {original_subject} - Recipme Support"
    preview_text = "We've responded to your message"
    
    html_content = f'''
        <h2 style="margin: 0 0 16px 0; font-size: 20px; font-weight: bold; color: #000000;">
            We've Responded to Your Message
        </h2>
        <p style="margin: 0 0 24px 0; font-size: 14px; color: #374151; line-height: 1.6;">
            Thank you for contacting Recipme Support. Here's our response to your inquiry:
        </p>
        
        <!-- Original message box -->
        <div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-radius: 6px; border: 1px solid #e5e7eb;">
            <p style="margin: 0 0 8px 0; font-size: 12px; font-weight: bold; color: #6b7280; text-transform: uppercase;">
                Your Original Message
            </p>
            <p style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #000000;">
                {original_subject}
            </p>
            <p style="margin: 0; font-size: 14px; color: #374151; line-height: 1.6; white-space: pre-wrap;">
{original_message}
            </p>
        </div>
        
        <!-- Response box -->
        <div style="margin-bottom: 24px; padding: 16px; background-color: #ffffff; border-radius: 6px; border: 2px solid #000000;">
            <p style="margin: 0 0 8px 0; font-size: 12px; font-weight: bold; color: #000000; text-transform: uppercase;">
                Our Response
            </p>
            <p style="margin: 0; font-size: 14px; color: #374151; line-height: 1.6; white-space: pre-wrap;">
{admin_response}
            </p>
        </div>
        
        <p style="margin: 0; font-size: 14px; color: #374151; line-height: 1.6;">
            If you have any further questions, feel free to reach out again through our Contact Us page.
        </p>
        
        <p style="margin: 24px 0 0 0; font-size: 14px; color: #374151;">
            Best regards,<br>
            <strong>The Recipme Team</strong>
        </p>
    '''
    
    plain_text = f"""
Re: {original_subject} - Recipme Support

Thank you for contacting Recipme Support. Here's our response to your inquiry:

---
YOUR ORIGINAL MESSAGE:

Subject: {original_subject}

{original_message}

---
OUR RESPONSE:

{admin_response}

---

If you have any further questions, feel free to reach out again.

Best regards,
The Recipme Team
"""
    
    return send_branded_email(subject, to_email, html_content, plain_text, preview_text)
