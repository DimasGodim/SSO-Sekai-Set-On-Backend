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
    verify_link = f"{config.origins_public}={target_email}"

    message_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Verifikasi Email</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Kiwi+Maru&display=swap" rel="stylesheet">
    </head>
    <body style="margin:0; padding:0; background-color:#0d0d0d; font-family: 'Kiwi Maru', sans-serif; color: #e0e0e0;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1a1a1a; border-radius: 12px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3); overflow: hidden;">
                        <tr>
                            <td style="background-color: #000; padding: 24px; text-align: center;">
                                <h1 style="margin: 0; font-size: 36px; color: #00ffff;">せかい</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 32px;">
                                <h2 style="margin-top: 0; font-size: 24px; color: #ffffff;">Verify Your Email Address</h2>
                                <p style="color: #cccccc;">Thank you for registering with <strong>せかい</strong>. Use the code below to complete your sign-up process:</p>
                                <div style="margin: 24px 0; padding: 16px; background-color: #111; border-left: 4px solid #00ffff; border-radius: 4px; text-align: center; font-size: 28px; font-weight: bold; color: #00ffff;">
                                    { verification_code }
                                </div>
                                <p style="color: #aaa;">Or verify directly using the button below:</p>
                                <div style="text-align: center; margin: 28px 0;">
                                    <a href="{ verify_link }" style="background-color: #00ffff; color: #000; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; display: inline-block;">
                                        Verify My Email
                                    </a>
                                </div>
                                <p style="font-size: 12px; color: #666;">If the button doesn't work, copy this link into your browser:</p>
                                <p style="font-size: 12px; color: #00ffff; word-break: break-word;">{ verify_link }</p>
                                <p style="margin-top: 32px; font-size: 14px; color: #999;">Best regards,<br><strong>せかい Team</strong></p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background-color: #111; padding: 16px; text-align: center; font-size: 12px; color: #555;">
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
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>API Key Created</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Kiwi+Maru&display=swap" rel="stylesheet">
    </head>
    <body style="margin:0; padding:0; background-color:#0d0d0d; font-family: 'Kiwi Maru', sans-serif; color: #e0e0e0;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1a1a1a; border-radius: 12px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3); overflow: hidden;">
                        <tr>
                            <td style="background-color: #000; padding: 24px; text-align: center;">
                                <h1 style="margin: 0; font-size: 36px; color: #00ffff;">せかい</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 32px;">
                                <h2 style="margin-top: 0; font-size: 24px; color: #ffffff;">API Key Created Successfully</h2>
                                <p style="color: #cccccc;">Hello,</p>
                                <p style="color: #cccccc;">
                                    Your API key titled <strong style="color:#00ffff;">{ title }</strong> has been created successfully on:
                                </p>
                                <div style="margin: 16px 0; padding: 12px; background-color: #111; border-left: 4px solid #00ffff; border-radius: 4px; font-size: 18px; color: #00ffff;">
                                    { str(created_at) }
                                </div>
                                <p style="color: #ccc;">
                                    Please keep your API key <strong>secure</strong> and do not share it with anyone.
                                </p>
                                <p style="margin-top: 24px; color: #aaa;">Thank you for using our service!</p>
                                <p style="color: #999; margin-top: 32px;">Best regards,<br><strong>せかい Team</strong></p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background-color: #111; padding: 16px; text-align: center; font-size: 12px; color: #555;">
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
            return True
    except Exception as e:
        print(f"Gagal mengirim email ke {email}: {e}")
