FROM python:3.10-alpine3.14

WORKDIR /app 

# # Update PATH environment variable to include Python binaries
# ENV PATH="/usr/local/bin:${PATH}"

# Copy general requirements
COPY requirements.txt .
COPY .env .
COPY utilities.py .

# Copy icon-getting script files
COPY get_latest_champion_icons.py .
COPY get_latest_item_icons.py .
COPY get_latest_major_rune_minor_rune_stat_mod_icons.py .
COPY get_latest_profile_icons.py .
COPY get_latest_summoner_spell_icons.py .


# Install cron and log rotate
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev openssl-dev logrotate

# Install requirements for python scripts
RUN pip install -r requirements.txt

# Copy cron definitions
COPY get_icons_cron /etc/cron.d/get_icons_cron
COPY logrotate_cron /etc/cron.d/logrotate_cron

# Copy log rotate configuration / rules for rotating logs
COPY logrotate.conf /etc/logrotate.d/

# Give execution permissions to cron job file & logrotate
RUN chmod 0644 /etc/cron.d/get_icons_cron /etc/cron.d/logrotate_cron

# Make directories & files for the job logs/volume to read from
RUN mkdir -p /var/log/icons \
    && touch /var/log/icons/champion_icons_job.log \
             /var/log/icons/item_icons_job.log \
             /var/log/icons/rune_icons_job.log \
             /var/log/icons/profile_icons_job.log \
             /var/log/icons/summoner_spell_icons_job.log


CMD ["crond", "-f"]
