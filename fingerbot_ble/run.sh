#!/usr/bin/env bash
set -e

echo "Starting Fingerbot BLE MQTT add-on..."

# Ejecutar el script Python con parámetros MQTT
python3 /fingerbot-mqtt.py --mqtt-broker "" --mqtt-topic ""

echo "Fingerbot BLE MQTT add-on finished."
