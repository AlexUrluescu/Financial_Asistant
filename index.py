from flask import Flask
from threading import Thread
import schedule
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from financial_agent import financial_agent

app = Flask(__name__)

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
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))  # Changed to str(e) instead of e.message which may not exist

# Schedule job
schedule.every().day.at("20:29").do(send_email)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def home():
    return 'Email Scheduler Running with Flask!'

if __name__ == '__main__':
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    app.run(debug=True, use_reloader=False)

