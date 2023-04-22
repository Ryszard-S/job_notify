import asyncio
import os
import random
import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiohttp
from dotenv import load_dotenv

from getOffers import get_offers_just, get_offers_bulldog, get_offers_pracuj, get_offers_nofluff
from templates import env

load_dotenv()


async def get_all(session):
    task1 = asyncio.create_task(get_offers_just(session))
    task2 = asyncio.create_task(get_offers_nofluff(session))
    task3 = asyncio.create_task(get_offers_bulldog(session))
    task4 = asyncio.create_task(get_offers_pracuj(session))
    tasks = [task1, task2, task3, task4]
    results = await asyncio.gather(*tasks)
    return results


async def zet():
    async with aiohttp.ClientSession() as session:
        data = await get_all(session)
        return data


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

resp = asyncio.run(zet())

pracuj = resp[3]
bulldog = resp[2]
just = resp[0]
nofluff = resp[1]

context = [{"name": "Pracuj", "offers": pracuj},
           {"name": "Bulldog", "offers": bulldog},
           {"name": "JustJoinIT", "offers": just},
           {"name": "NoFluff", "offers": nofluff}, ]

message_html = template.render(context=context)

part1 = MIMEText(message_text, "plain")
part2 = MIMEText(message_html, "html")

message.attach(part1)
message.attach(part2)

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
