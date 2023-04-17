# Job Offer Notify Emails
This is a Python app that sends job offer notification emails to users. The email content is generated using Jinja2 templates.

## Installation
Clone the repo:

```bash
git clone https://github.com/your_username/job-offer-notify-emails.git
```
Build the Docker container:

```bash
docker build -t job-offer-notify-emails .
```
Run the Docker container:

```bash
docker run -d -p 8000:8000 job-offer-notify-emails
```
or you can use docker compose:
```bash
docker compose up
```
Usage
 - EMAIL1 sender email with smtp protocol
 - EMAIL2 reciver email
 - PASSWORD sender email password

## Technology used:
    - Python
    - Jinja2
    - Docker
    - Docker Compose
    - SMTP
    - HTML
    - CSS

currently the app is running on fly.io
