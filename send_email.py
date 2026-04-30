import os
from dotenv import load_dotenv
import yagmail

load_dotenv()

yag = yagmail.SMTP(os.getenv('GMAIL_ID'), os.getenv('APP_PASSWORD'))
# get otp 
yag.send(
    to='jha.anurag2017@outlook.com',
    subject='Hello from yagmail',
    contents=f'OTP: {}'
)

# 15 minute valid otp