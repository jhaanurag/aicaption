import os
from dotenv import load_dotenv
import yagmail

load_dotenv()

yag = yagmail.SMTP(os.getenv('GMAIL_ID'), os.getenv('APP_PASSWORD'))

yag.send(
    to='jha.anurag2017@outlook.com',
    subject='Hello from yagmail',
    contents='This is the body of the email.'
)
