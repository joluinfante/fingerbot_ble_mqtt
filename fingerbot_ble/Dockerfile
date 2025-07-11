FROM ghcr.io/home-assistant/raspberrypi4-64-homeassistant-base:latest

# Install python3 and bluez tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bluez \
    bluez-libs \
    bluez-dev \
    dbus

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy add-on files
COPY run.sh /run.sh
COPY fingerbot-mqtt.py /fingerbot-mqtt.py

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

