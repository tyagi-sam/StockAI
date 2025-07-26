import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from ..core.config import settings
from ..core.logger import logger

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.smtp_ssl = settings.SMTP_SSL
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
    
    def _create_message(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> MIMEMultipart:
        """Create email message"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        
        # Add text and HTML parts
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        return message
    
    def _send_email(self, message: MIMEMultipart) -> bool:
        """Send email via SMTP"""
        try:
            if self.smtp_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.smtp_tls:
                        server.starttls()
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False
    
    def send_verification_otp(self, to_email: str, otp: str, name: str = None) -> bool:
        """Send verification OTP email"""
        subject = "Verify Your Email - StockAI"
        
        # HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: #fff; border: 2px solid #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 StockAI</h1>
                    <p>Email Verification</p>
                </div>
                <div class="content">
                    <h2>Hello{f" {name}" if name else ""}!</h2>
                    <p>Thank you for registering with StockAI. To complete your registration, please use the verification code below:</p>
                    
                    <div class="otp-box">
                        <div class="otp-code">{otp}</div>
                        <p><strong>Verification Code</strong></p>
                    </div>
                    
                    <p>This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
                    
                    <p>If you didn't create an account with StockAI, please ignore this email.</p>
                    
                    <p>Best regards,<br>The StockAI Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2024 StockAI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text content
        text_content = f"""
        Hello{f" {name}" if name else ""}!
        
        Thank you for registering with StockAI. To complete your registration, please use the verification code below:
        
        Verification Code: {otp}
        
        This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.
        
        If you didn't create an account with StockAI, please ignore this email.
        
        Best regards,
        The StockAI Team
        
        ---
        This is an automated message, please do not reply to this email.
        © 2024 StockAI. All rights reserved.
        """
        
        message = self._create_message(to_email, subject, html_content, text_content)
        return self._send_email(message)
    
    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email after successful verification"""
        subject = "Welcome to StockAI! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to StockAI</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 StockAI</h1>
                    <p>Welcome Aboard!</p>
                </div>
                <div class="content">
                    <h2>Welcome to StockAI, {name}! 🎉</h2>
                    <p>Your email has been successfully verified and your account is now active.</p>
                    
                    <p>You can now:</p>
                    <ul>
                        <li>📊 Analyze stocks with AI-powered insights</li>
                        <li>📈 Get technical analysis and recommendations</li>
                        <li>🔍 Access real-time market data</li>
                        <li>💡 Receive intelligent trading suggestions</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="{settings.FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
                    </p>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Happy trading!<br>The StockAI Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2024 StockAI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to StockAI, {name}! 🎉
        
        Your email has been successfully verified and your account is now active.
        
        You can now:
        - Analyze stocks with AI-powered insights
        - Get technical analysis and recommendations
        - Access real-time market data
        - Receive intelligent trading suggestions
        
        Visit your dashboard: {settings.FRONTEND_URL}/dashboard
        
        If you have any questions, feel free to reach out to our support team.
        
        Happy trading!
        The StockAI Team
        
        ---
        This is an automated message, please do not reply to this email.
        © 2024 StockAI. All rights reserved.
        """
        
        message = self._create_message(to_email, subject, html_content, text_content)
        return self._send_email(message)

# Create email service instance
email_service = EmailService() 