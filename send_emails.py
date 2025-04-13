import schedule
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from financial_agent import financial_agent
import os

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email():

    news_content = financial_agent()

    formatted_news = news_content.replace("\n", "<br>")
    html_content = f'<strong>Here is your financial news summary:</strong><br><br>{formatted_news}'

    message = Mail(
        from_email='alexandre.urluescu@mtdtechnology.net',
        to_emails='alexurluescu23@gmail.com',
        subject='Daily Financial News Summary',
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

schedule.every().day.at("16:52").do(send_email)

while True:
    schedule.run_pending()
    time.sleep(60)  
