import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from config import * 


def send_inline_notification_email(filename, month):
    # 1. Create a "related" multipart message container for inline images
    msg = MIMEMultipart('related')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"Updated calendar for {month}"

    # 2. Define the HTML body referencing the image via its Content-ID (cid)
    html_body = """
    <html>
      <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
        <p>An internal comparison check noticed an update to your VRBO booking roster.</p>
        <p>The current operational month footprint is displayed directly below:</p>
        <br>
        <div style="text-align: left;">
            <img src="cid:vrbo_calendar_image" alt="VRBO Calendar" style="max-width: 100%; border: 1px solid #cbd5e1; border-radius: 8px;">
        </div>
        <br>
        <p style="font-size: 12px; color: #64748b;">This is an automated system notification.</p>
      </body>
    </html>
    """
    
    # Attach the HTML content text to the message container
    msg_html = MIMEText(html_body, 'html')
    msg.attach(msg_html)

    # 3. Read the image file and attach it as an inline resource
    try:
        with open(filename, 'rb') as img_file:
            msg_image = MIMEImage(img_file.read())
            
        # Define the Content-ID. This must exactly match the string in <img src="cid:...">
        msg_image.add_header('Content-ID', '<vrbo_calendar_image>')
        # Inform email clients not to show this as a traditional downloadable attachment
        msg_image.add_header('Content-Disposition', 'inline', filename=filename)
        msg.attach(msg_image)
        
    except Exception as e:
        print(f"Error packing image asset: {e}")
        return

    # 4. Connect to server and transmit
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("Inline notification email dispatched successfully.")
    except Exception as e:
        print(f"Failed to transmit email package: {e}")

if __name__ == "__main__":
    send_inline_notification_email()
