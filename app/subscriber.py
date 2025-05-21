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

print(f'BROKER_ADDRESS: {os.getenv("BROKER_ADDRESS")}')
print(f'BROKER_PORT: {os.getenv("BROKER_PORT")}')
print(f'BROKER_USERNAME: {os.getenv("BROKER_USERNAME")}')
print(f'BROKER_PASSWORD: {os.getenv("BROKER_PASSWORD")}')
print(f'DB_DATABASE: {os.getenv("DB_DATABASE")}')
print(f'DB_USER: {os.getenv("DB_USER")}')
print(f'DB_PASSWORD: {os.getenv("DB_PASSWORD")}')
print(f'DB_HOST: {os.getenv("DB_HOST")}')
print(f'DB_PORT: {os.getenv("DB_PORT")}')

# Define the MQTT broker parameters
broker_address = os.getenv("BROKER_ADDRESS")
broker_port = os.getenv("BROKER_PORT")
username = os.getenv("BROKER_USERNAME")
password = os.getenv("BROKER_PASSWORD")

topic = "sensors"

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

    ts_data = TSData.TSData.GetRootAs(buffer, 0)

    # TODO parse flatbuffers file dynamically by reading ts_data.fbs
    cursor.execute(
        "INSERT INTO measurements (time, vehicle_type, fc_voltage, fc_current, fc_temperature, sc_motor_voltage, sc_current, motor_current, motor_speed, motor_pwm, vehicle_speed, h2_pressure, h2_leak_level, fan_rpm, gps_latitude, gps_longitude, gps_altitude, gps_speed, lap_number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (tm.time(), '0', ts_data.FcVoltage(), ts_data.FcCurrent(), ts_data.FuelCellTemperature(), ts_data.ScVoltage(),
         ts_data.FcScCurrent(), ts_data.MotorCurrent(), ts_data.MotorSpeed(), ts_data.MotorPwm(), ts_data.VehicleSpeed(),
         ts_data.HydrogenPressure(), '2', ts_data.FanRpm(), ts_data.GpsLatitude(), ts_data.GpsLongitude(),
         ts_data.GpsAltitude(), ts_data.GpsSpeed(), ts_data.LapNumber()))

    conn.commit()

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

    cursor = conn.cursor()

    # Create an MQTT client
    new_client = mqtt.Client()

    # Set the username and password for authentication
    new_client.username_pw_set(username=username, password=password)

    # Connect to the broker
    new_client.connect(host=broker_address, port=int(broker_port))

    # Subscribe to the topic
    new_client.subscribe(topic, options=SubscribeOptions(qos=2))

    # Define the callback function to handle incoming messages
    new_client.on_message = on_message

    # Start the loop to receive messages
    new_client.loop_forever()


except Exception as e:
    print("Error: ", e)

finally:
    cursor.close()
    conn.close()
    new_client.disconnect()
