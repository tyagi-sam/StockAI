#!/usr/bin/env python3
"""
Test script to verify Zoho Mail SMTP configuration
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_zoho_smtp():
    """Test Zoho SMTP connection and authentication"""
    
    # Configuration - Update these with your actual values
    smtp_host = "smtppro.zoho.in"  # For domain-based accounts
    smtp_port = 587  # TLS port
    smtp_username = "noreply@stock-satta.online"  # Your email
    smtp_password = "YOUR_ZOHO_PASSWORD_HERE"  # Your password
    
    print("🔧 Testing Zoho Mail SMTP Configuration")
    print("=" * 50)
    
    try:
        # Test 1: Connection
        print("1. Testing connection...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        print("   ✅ Connected to SMTP server")
        
        # Test 2: TLS
        print("2. Testing TLS...")
        server.starttls()
        print("   ✅ TLS enabled")
        
        # Test 3: Authentication
        print("3. Testing authentication...")
        server.login(smtp_username, smtp_password)
        print("   ✅ Authentication successful")
        
        # Test 4: Send test email
        print("4. Testing email send...")
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Stock AI - SMTP Test"
        message["From"] = f"StockAI <{smtp_username}>"
        message["To"] = "test@example.com"  # Change this to your test email
        
        # Add content
        text_content = "This is a test email from Stock AI application."
        html_content = f"""
        <html>
        <body>
            <h2>Stock AI SMTP Test</h2>
            <p>This is a test email from Stock AI application.</p>
            <p>If you receive this, your SMTP configuration is working correctly!</p>
        </body>
        </html>
        """
        
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email
        server.send_message(message)
        print("   ✅ Test email sent successfully!")
        
        # Close connection
        server.quit()
        print("   ✅ Connection closed")
        
        print("\n🎉 All tests passed! Your Zoho Mail SMTP is working correctly.")
        print("\n📝 Update your .env file with these settings:")
        print(f"SMTP_HOST={smtp_host}")
        print(f"SMTP_PORT={smtp_port}")
        print(f"SMTP_USERNAME={smtp_username}")
        print(f"SMTP_PASSWORD={smtp_password}")
        print("SMTP_TLS=true")
        print("SMTP_SSL=false")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("\n💡 Solutions:")
        print("1. Check if your password is correct")
        print("2. If you have 2FA enabled, generate an app-specific password")
        print("3. Make sure you're using the correct email address")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n💡 Solutions:")
        print("1. Check if the SMTP host is correct (smtppro.zoho.in)")
        print("2. Check if the port is correct (587 for TLS)")
        print("3. Check your internet connection")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Update the script with your actual credentials before running!")
    print("1. Change smtp_username to your email")
    print("2. Change smtp_password to your password")
    print("3. Change the 'To' email address to your test email")
    print("\nThen run: python3 test_email_config.py")
    
    # Uncomment the line below after updating credentials
    # test_zoho_smtp() 