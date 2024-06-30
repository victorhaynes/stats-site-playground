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
COPY get_latest_runes_icons.py .
COPY get_latest_profile_icons.py .
COPY get_latest_summoner_spells_icons.py .

# Copy asset-detail-getting script files
COPY get_latest_champion_details.py .
COPY get_latest_game_modes_details.py .
COPY get_latest_item_details.py .
COPY get_latest_runes_details.py .
COPY get_latest_summoner_spells_details.py .


# Install cron and log rotate
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev openssl-dev logrotate

# Install requirements for python scripts
RUN pip install -r requirements.txt

# Copy cron definitions
COPY get_icons_cron /etc/cron.d/get_icons_cron
COPY get_details_cron /etc/cron.d/get_details_cron
COPY logrotate_cron /etc/cron.d/logrotate_cron

# Copy log rotate configuration / rules for rotating logs
COPY logrotate.conf /etc/logrotate.d/

# Give execution permissions to cron job files & logrotate
RUN chmod 0644 /etc/cron.d/get_icons_cron \
    && chmod 0644 /etc/cron.d/get_details_cron \
    && chmod 0644 /etc/cron.d/logrotate_cron

# Make directories & files for the job logs/volume to read from
RUN mkdir -p /var/log/icons \
    && touch /var/log/icons/champion_icons_job.log \
             /var/log/icons/item_icons_job.log \
             /var/log/icons/rune_icons_job.log \
             /var/log/icons/profile_icons_job.log \
             /var/log/icons/summoner_spell_icons_job.log \
    && mkdir -p /var/log/game_content \
    && touch /var/log/game_content/champion_details_job.log \
             /var/log/game_content/game_mode_details_job.log \
             /var/log/game_content/item_details_job.log \
             /var/log/game_content/rune_details_job.log \
             /var/log/game_content/summoner_spell_details_job.log


CMD ["crond", "-f"]
