import requests
from icalendar import Calendar
from datetime import datetime, date
import calendar
import argparse
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import io
import os
from config import * 

# URL for the iCalendar
ICAL_URL = "http://www.vrbo.com/icalendar/665c292bce1b41c7b1180a35222059f1.ics?nonTentative"

# Email configuration (replace with your details)
#SMTP_SERVER = "smtp.gmail.com"
#SMTP_PORT = 587


#SENDER_EMAIL = "your email"
#SENDER_PASSWORD = "your password"
#RECIPIENT_EMAIL = "default recipient email"



def fetch_ical_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return Calendar.from_ical(response.text)

def get_current_month_reservations(cal, year, month):
    reservations = []
    
    for component in cal.walk():
        if component.name == "VEVENT":
            start_date = component.get("dtstart").dt
            end_date = component.get("dtend").dt
            # Handle both datetime and date objects
            if isinstance(start_date, datetime):
                start_date = start_date.date()
                end_date = end_date.date()
            prevmonth = month -1 
            if (prevmonth == 0):
               prevmonth = 12 
       
            # Filter for the specified month
            if start_date.year == year and (start_date.month == month or (start_date.month == prevmonth and end_date.month == month)):
                summary = component.get("summary", "Unknown Guest").replace(" - ", " ")
                print(start_date.day, start_date.month, end_date.day,end_date.month)
                reservations.append((start_date.day, start_date.month, end_date.day,end_date.month,  summary))
    
    return reservations

def create_calendar_image(year, month, reservations):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Set first weekday to Sunday (0) to match the example
    calendar.setfirstweekday(6)  # 6 = Sunday
    cal = [week for week in calendar.monthcalendar(year, month)]
    
    # Image dimensions (matching the example layout)
    cell_size = 60
    width = 7 * cell_size + 20
    height = (len(cal) + 2) * cell_size + 40
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        bold_font = ImageFont.truetype("arial.tf", 20)  # Bold font for headers and names
    except:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default(20)
        days_font = ImageFont.load_default(16)
    
    # Draw month and year
    draw.text((10, 10), f"{month_name} {year}", fill="black", font=bold_font)
    
    # Draw day headers
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, day in enumerate(days):
        draw.text((10 + i * cell_size, 40), day, fill="black", font=days_font)
    
    # Draw calendar grid and numbers
    for week_idx, week in enumerate(cal):
        for day_idx, day in enumerate(week):
            if day != 0:
                x = 10 + day_idx * cell_size
                y = 70 + week_idx * cell_size
#               draw.rectangle((x, y, x + cell_size - 2, y + cell_size - 2), outline="black", width=1)
                draw.rectangle((x, y, x + cell_size - 2, y + cell_size - 2), fill="#85a2ed")
                draw.text((x + 5, y + 5), str(day), fill="black", font=font)
    
#   # Add sample prices (replace with actual pricing logic if available in iCalendar)
#   base_price = 225  # Example base price, adjust as needed
#   for week_idx, week in enumerate(cal):
#       for day_idx, day in enumerate(week):
#           if day != 0:
#               x = 10 + day_idx * cell_size
#               y = 70 + week_idx * cell_size
#               price = f"${base_price + day % 10}"
#               draw.text((x + 5, y + 25), price, fill="black", font=font)
    
    # Highlight reservations with thick blue lines and guest names
    for start_day, start_month, end_day, end_month, guest in reservations:
        print(start_day, " ", end_day)
        guest = guest.replace("Reserved ","")
        step = 1 
        # stay begins previous month
#       if end_day < start_day and start_month < : 
#           step = -1  
#           start_day = 1

        # stay ends next month
        print(f" end_day < start_day and end_month > start_month")
        print(f" {end_day} < {start_day} and {end_month} > {start_month}")
        if end_day < start_day and (end_month > start_month or end_month ==1 and start_month ==12):
           
           print(f" month = {month} end_month = {end_month} ")
           if month == end_month:
              start_day = 0
              print('setting start_day = 0')
           if month == start_month:
              end_day = 32  

        
        for day in range(start_day, end_day + 1, step):
            for week_idx, week in enumerate(cal):
                if day in week:
                    day_idx = week.index(day)
                    print(day)
                    x = 10 + day_idx * cell_size
                    y = 70 + week_idx * cell_size
                    # Draw thick blue outline for reserved days

                    if day == start_day:
                        draw.line((x + 2*cell_size/3 , y + cell_size/2, x + cell_size, y + cell_size / 2), fill="blue", width=3)
                    elif day == end_day:
                        draw.line((x , y + cell_size/2 , x + cell_size/3, y + cell_size / 2), fill="blue", width=3)
                    else:
                        draw.line((x , y + cell_size/2, x + cell_size, y + cell_size / 2), fill="blue", width=3)
                        draw.text((x + 5, y + 45), guest[:10] + "..." if len(guest) > 10 else guest, fill="black", font=font, align="right")


    
    # Save image to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()

def send_email_with_calendar(image_data, year, month, email=RECIPIENT_EMAIL):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = email 
    msg["Subject"] = f"4202 Calendar for {calendar.month_name[month]} {year}"
    
    # Attach image
    image = MIMEImage(image_data, name=f"calendar_{year}_{month}.jpg")
    msg.attach(image)
    
    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate and email a calendar for a specified month.")
    parser.add_argument("--month", type=int, choices=range(1, 13), help="Month number (1-12)")
    parser.add_argument("--nextmonth", type=bool, help="")
    parser.add_argument("--email", help="recipient email")
    parser.add_argument("--year", type=int, help="Year (e.g., 2025)")
    args = parser.parse_args()

    # Get current date if no arguments provided
    today = datetime.now()
    year = args.year if args.year else today.year
    month = args.month if args.month else today.month
    if args.nextmonth:
      month = month +1
      if month == 13: 
         month = 1

    if args.email != "":
       email = args.email


    # Validate month
    if month < 1 or month > 12:
        print("Month must be between 1 and 12.")
        return

    # Fetch and parse iCalendar data
    cal = fetch_ical_data(ICAL_URL)
    
    # Get reservations for the specified month
    reservations = get_current_month_reservations(cal, year, month)
    
    # Create calendar image
    calendar_image = create_calendar_image(year, month, reservations)
    
    # Send email with calendar
    send_email_with_calendar(calendar_image, year, month, email)
    print(f"Calendar for {calendar.month_name[month]} {year} has been emailed.")

if __name__ == "__main__":
    main()
