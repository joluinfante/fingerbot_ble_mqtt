#!/usr/bin/env python3
import asyncio
import argparse
from bleak import BleakClient, BleakScanner
import paho.mqtt.client as mqtt

FINGERBOT_SERVICE_UUID = "0000fee7-0000-1000-8000-00805f9b34fb"
FINGERBOT_WRITE_CHAR_UUID = "d44bc439-abfd-45a2-b575-925416129600"

class Fingerbot:
    def __init__(self, address):
        self.address = address
        self.client = BleakClient(address)

    async def connect(self):
        await self.client.connect()

    async def disconnect(self):
        await self.client.disconnect()

    async def press(self):
        # Comando para pulsar el Fingerbot
        await self.client.write_gatt_char(FINGERBOT_WRITE_CHAR_UUID, bytearray([0xA0, 0x01, 0x01, 0x01, 0x00]))

    async def release(self):
        # Comando para soltar el Fingerbot
        await self.client.write_gatt_char(FINGERBOT_WRITE_CHAR_UUID, bytearray([0xA0, 0x01, 0x01, 0x00, 0x00]))

async def scan_fingerbot():
    devices = await BleakScanner.discover()
    for d in devices:
        if FINGERBOT_SERVICE_UUID.lower() in [s.lower() for s in d.metadata.get("uuids", [])]:
            return d.address
    return None

async def handle_command(fingerbot, command):
    if command == "PRESS":
        await fingerbot.press()
    elif command == "RELEASE":
        await fingerbot.release()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mqtt-broker", default="mqtt://core-mosquitto")
    parser.add_argument("--mqtt-topic", default="fingerbot")
    args = parser.parse_args()

    mqtt_broker = args.mqtt_broker
    mqtt_topic = args.mqtt_topic

    fingerbot_address = None

    loop = asyncio.get_event_loop()

    def on_connect(client, userdata, flags, rc):
        print("Connected to MQTT broker")
        client.subscribe(f"{mqtt_topic}/command")

    def on_message(client, userdata, msg):
        cmd = msg.payload.decode().upper()
        print(f"Received MQTT message: {cmd}")

        if fingerbot_address:
            async def run_cmd():
                fingerbot = Fingerbot(fingerbot_address)
                await fingerbot.connect()
                await handle_command(fingerbot, cmd)
                await fingerbot.disconnect()
            loop.create_task(run_cmd())
        else:
            print("Fingerbot not found yet.")

    async def runner():
        nonlocal fingerbot_address
        print("Scanning for Fingerbot BLE device...")
        fingerbot_address = await scan_fingerbot()
        if fingerbot_address:
            print(f"Found Fingerbot at {fingerbot_address}")
        else:
            print("Fingerbot not found. Please make sure it is powered on and nearby.")

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        # Parse mqtt broker URL (simple http:// or mqtt://) support
        if mqtt_broker.startswith("mqtt://"):
            broker = mqtt_broker[len("mqtt://"):]
            port = 1883
        else:
            broker = mqtt_broker
            port = 1883

        client.connect(broker, port, 60)
        client.loop_start()

        while True:
            await asyncio.sleep(1)

    try:
        loop.run_until_complete(runner())
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
 


