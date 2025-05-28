import re
import sys
import time as tm
import datetime
import os
import struct
import numpy as np

import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions

import psycopg2

import flatbuffers
import TSData
import FuelCellMode

from tempfile import SpooledTemporaryFile
import capnp
#import ts_data_capnp

capnp.remove_import_hook()
ts_data_capnp = capnp.load('./ts_data.capnp')

# Define the MQTT broker parameters
broker_address = os.getenv("BROKER_ADDRESS")
broker_port = os.getenv("BROKER_PORT")
username = os.getenv("BROKER_USERNAME")
password = os.getenv("BROKER_PASSWORD")

topic = "sensors"

def to_snake_case(name):
    """Converts a CamelCase string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def on_message(client, userdata, msg):
    buffer = bytearray(msg.payload)

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # [:-3] to get milliseconds instead of microseconds
    print(f"=== Message received - {len(buffer)} bytes - {timestamp} (UTC) ===")
    print(buffer.hex(sep=' '))

    required_bytes = 128

    if len(buffer) != required_bytes:
        print(f"Required value not reached: frame save aborted (bytes: {len(buffer)}/{required_bytes})")
        return

    ts_data_flatbuffers = TSData.TSData.GetRootAs(buffer)
    print(f"[Data check - FlatBuffers] Latitude: {ts_data_flatbuffers.GpsLatitude()}, Longitude: {ts_data_flatbuffers.GpsLongitude()}")

    f = SpooledTemporaryFile(256, 'wb+')
    f.write(buffer)
    f.seek(0)
    data = ts_data_capnp.TSData.read(f)
    ts_data = data.to_dict()
    print(f"[Data check - Capnp] Latitude: {ts_data["gpsLatitude"]}, Longitude: {ts_data["gpsLongitude"]}")

    snake_case_data = {to_snake_case(key): value for key, value in ts_data.items()}

    column_names_str = ", ".join(snake_case_data)
    placeholders_str = ", ".join(["%s"] * len(snake_case_data))

    query = (
        f"INSERT INTO measurements ({column_names_str}) "
        f"VALUES ({placeholders_str}) "
        "ON CONFLICT DO NOTHING"
    )
    values = tuple(value for key, value in ts_data.items())

    cursor.execute(query, values)
    conn.commit()

try:
    print("=== PROGRAM START ===")
    print(f'BROKER_ADDRESS: {os.getenv("BROKER_ADDRESS")}')
    print(f'BROKER_PORT: {os.getenv("BROKER_PORT")}')
    print(f'DB_DATABASE: {os.getenv("DB_DATABASE")}')
    print(f'DB_HOST: {os.getenv("DB_HOST")}')
    print(f'DB_PORT: {os.getenv("DB_PORT")}')

    conn = psycopg2.connect(
        dbname=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    print("Database connection was successful")

    cursor = conn.cursor()

    # Create an MQTT client
    new_client = mqtt.Client()

    # Set the username and password for authentication
    new_client.username_pw_set(username=username, password=password)

    # Connect to the broker
    new_client.connect(host=broker_address, port=int(broker_port))
    print("MQTT connection was successful")

    # Subscribe to the topic
    new_client.subscribe(topic, options=SubscribeOptions(qos=2))

    # Define the callback function to handle incoming messages
    new_client.on_message = on_message

    # Start the loop to receive messages
    new_client.loop_forever()


except Exception as e:
    print("Error:", e)

finally:
    cursor.close()
    conn.close()
    new_client.disconnect()
