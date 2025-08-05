from calendar_utils import * 
from config import * 

# The following constants should be defined in your config.py file
# URL for the iCalendar
# ICAL_URL = "http://www.vrbo.com/icalendar/yourkey"

# Email configuration (replace with your details)
#SMTP_SERVER = "smtp.gmail.com"
#SMTP_PORT = 587

#SENDER_EMAIL = "your email"
#SENDER_PASSWORD = "your password"
#RECIPIENT_EMAIL = "default recipient email"

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
 
    # Drop calendar image to local dir 
    try: 
        with open(f"vrbo_calendar_{year}-%02d.jpg" % month, "wb") as outfh: 
           outfh.write(calendar_image)
    except Exception as e:
        print("cannot write image file to local dir")
        print(e)
        
    
    # Send email with calendar
    send_email_with_calendar_inline(calendar_image, year, month, email)
    #send_email_with_calendar_attached(calendar_image, year, month, email)
    print(f"Calendar for {calendar.month_name[month]} {year} has been emailed.")

if __name__ == "__main__":
    main()
