import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.configs import config  

SERVER = 'smtp.gmail.com'
PORT = 587
MY_EMAIL = config.email
MY_PASSWORD = config.password_email

def send_verivication_code(target_email: str, verification_code: str):
    msg = MIMEMultipart()

    subject = "Verifikasi Email untuk せかい (SSO)"
    sender_name = "せかい Team"
    sender_email = "no-reply@sekaiseton.com"  # Bisa ganti sesuai domain kamu

    message_body = f"""
    <html>
    <body style="margin:0; padding:0; font-family: 'Arial'; background-color:#f5f7fa;">
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td align="center" style="padding: 40px 0;">
            <table width="600" cellpadding="0" cellspacing="0" style="background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">
                <tr>
                <td style="background-color: #a6a6a6; padding: 24px; text-align: center; color: rgba(255, 255, 255, 0.7);;">
                    <table align="center" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                        <tr>
                            <td>
                                <img src="https://i.imgur.com/ja3Ii9K.png" alt="せかい Logo" style="height: 63px; vertical-align: middle; margin-right: 12px;" />
                            </td>
                            <td>
                                <h1 style="margin: 0; font-size: 36px; font-family: 'Arial', sans-serif; font-weight: 300;">せかい</h1>
                            </td>
                        </tr>
                    </table>
                </td>
                </tr>
                <tr>
                <td style="padding: 32px;">
                    <h2 style="color: #333; margin-top: 0;">Verify Your Email Address</h2>
                    <p>Thank you for registering with <strong>せかい</strong>. Please use the verification code below to complete your sign-up process:</p>
                    <div style="margin: 20px 0; padding: 16px; background-color: #f0f0f0; border-radius: 4px; text-align: center; font-size: 24px; font-weight: bold; color: #111;">
                    {verification_code}
                    </div>
                    <p style="font-size: 14px; color: #666;">
                    This code is temporary and will expire shortly. If you did not request this verification, please ignore this message.
                    </p>
                    <p style="margin-top: 32px; font-size: 14px; color: #444;">Best regards,<br><strong>せかい Team</strong></p>
                </td>
                </tr>
                <tr>
                <td style="background-color: #f0f0f0; padding: 16px; text-align: center; font-size: 12px; color: #888;">
                    &copy; 2025 せかい. All rights reserved.
                </td>
                </tr>
            </table>
            </td>
        </tr>
        </table>
    </body>
    </html>
    """

    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = target_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'html'))
    server = smtplib.SMTP(SERVER, PORT)
    try:
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.sendmail(sender_email, target_email, msg.as_string())
        return True
    except Exception as e:
        print('Terjadi kesalahan:', str(e))
        return str(e)
    finally:
        server.quit()

def send_api_key_created_email(email: str, title: str, created_at: datetime):
    # Membuat subject dan isi email
    subject = "API Key Created Successfully"
    body = f"""
    Hello,

    Your API key titled {title} has been created successfully on {created_at.strftime('%Y-%m-%d %H:%M:%S')}.
    
    Please keep your API key secure and do not share it with others.
    
    Thank you for using our service!

    Regards,
    Sekai Set On Team
    """

    # Menyusun email
    msg = MIMEMultipart()
    msg["From"] = MY_EMAIL
    msg["To"] = email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Kirim email
    try:
        with smtplib.SMTP(SERVER, PORT) as server:
            server.starttls()
            server.login(MY_EMAIL, MY_PASSWORD)
            server.sendmail(MY_EMAIL, email, msg.as_string())
        print(f"✅ Email berhasil dikirim ke {email}")
    except Exception as e:
        print(f"Gagal mengirim email ke {email}: {e}")
