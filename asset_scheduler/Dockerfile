FROM python:3.10-alpine3.14

WORKDIR /app 

# # Update PATH environment variable to include Python binaries
# ENV PATH="/usr/local/bin:${PATH}"

COPY get_latest_champion_icons.py .
COPY requirements.txt .
COPY .env .

# Install cron
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev openssl-dev

RUN pip install -r requirements.txt

COPY cron_definition /etc/cron.d/cron_definition

# Give execution permissions to cron job file
RUN chmod 0644 /etc/cron.d/cron_definition

RUN crontab /etc/cron.d/cron_definition

RUN touch /var/log/cron.log

CMD ["crond", "-f"]
