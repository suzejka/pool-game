import smtplib
import os
import traceback 
from models.models import Idea
from unidecode import unidecode
from services import database_service as db

ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")

def send_error_email(exception, traceback, user=None):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(ALERT_EMAIL, ALERT_EMAIL_PASSWORD)
    message = f"""Subject:  {exception}

        User: {user}

        Error: {traceback}
    """
    s.sendmail(ALERT_EMAIL, ALERT_EMAIL, message)
    s.quit()

def send_idea_email(idea: Idea):
    user = db.get_user_by_id(idea.user_id)
    normalized = normalize_polish_characters(idea.description)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(ALERT_EMAIL, ALERT_EMAIL_PASSWORD)
    message = f"""Subject: New Idea

        {user.username} added a new {idea.type}: 
        {normalized}

    """
    s.sendmail(ALERT_EMAIL, ALERT_EMAIL, message)
    s.quit()

def normalize_polish_characters(text):
    normalized = unidecode(text)
    return normalized