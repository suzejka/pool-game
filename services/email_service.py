import smtplib
import os
import traceback 
  

ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")

def send_alert_email(exception, traceback, user=None):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(ALERT_EMAIL, ALERT_EMAIL_PASSWORD)
    message = f"""Subject:  {exception}

        User: {user}

        Error: {traceback}
    """
    s.sendmail(ALERT_EMAIL, ALERT_EMAIL, message)
    s.quit()