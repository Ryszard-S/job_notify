import os
import random
import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from getOffers import get_offers_just, get_offers_bulldog, get_offers_pracuj
from templates import env

load_dotenv()
sender_email = os.getenv("EMAIL1")
receiver_email = os.getenv("EMAIL2")
password = os.getenv("PASSWORD")

smtp_server = "smtp.poczta.onet.pl"
port = 465

message = MIMEMultipart("alternative")
date = date.today()
rand = random.randint(1, 100)
message["Subject"] = "Job alert " + date.strftime("%d-%m-%Y") + " " + str(rand)
message["From"] = sender_email
message["To"] = receiver_email

message_text = "Sth went wrong !"

template = env.get_template("email.html")

pracuj = get_offers_pracuj()
bulldog = get_offers_bulldog()
just = get_offers_just()

message_html = template.render(pracuj=pracuj, bulldog=bulldog, just=just)

part1 = MIMEText(message_text, "plain")
part2 = MIMEText(message_html, "html")

message.attach(part1)
message.attach(part2)

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
