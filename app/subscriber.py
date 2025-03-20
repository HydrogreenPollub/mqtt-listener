
# import paho.mqtt.client as mqtt

import psycopg2

import struct
import numpy as np
from numpy.random import default_rng
import flatbuffers
# from flatc-generated files
import TSData
import FuelCellMode

import sys
import time
import amqp
import os


print(os.getenv("BROKER_ADDRESS"))
print(os.getenv("USERNAME"))
print(os.getenv("PASSWORD"))
print(os.getenv("DBNAME"))
print(os.getenv("USER"))
print(os.getenv("DB_PASSWORD"))
print(os.getenv("HOST"))


# Define the RabbitMQ broker parameters
broker_address = os.getenv("BROKER_ADDRESS")
broker_port  = 5672
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
conn_address = str(broker_address)+":"+str(broker_port)


topic = "/sensors"

duration = 10*1000
sampling_rate = 100/1000  
amplitude =1
frequency = 1/1000
noise_level = 0.1

t0=1733939032


try:
    conn = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("HOST"),
        port="5432"
    )
    cursor = conn.cursor()

    # nie wiem czy nawet potrzebne
    time = np.arange(t0, t0+duration, 1/sampling_rate)
    signal = amplitude * np.sin(2 * np.pi * frequency * time)
    noisy_signal = signal + np.random.normal(0, noise_level, len(time))


# Define the callback function to handle incoming messages
    def on_message(message):
        print('Received message (delivery tag: {}): {}'.format(message.delivery_tag, message.body))
        buf = bytearray(message.body)
        tsdata = TSData.TSData.GetRootAs(buf,0)
        print(tsdata.FcVoltage())



    # Wstawianie danych
    
        cursor.execute("INSERT INTO measurements (time, vehicle_type, fc_voltage, fc_current, fc_temperature, sc_motor_voltage, sc_current, motor_current, motor_speed, motor_pwm, vehicle_speed, h2_pressure, h2_leak_level, fan_rpm, gps_latitude, gps_longitude, gps_altitude, gps_speed, lap_number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (time.time(),'0',tsdata.FcVoltage(),tsdata.FcCurrent(),tsdata.FuelCellTemperature(),tsdata.ScVoltage(),tsdata.FcScCurrent(),tsdata.MotorCurrent(),tsdata.MotorSpeed(),tsdata.MotorPwm(),tsdata.VehicleSpeed(),tsdata.HydrogenPressure(),'2',tsdata.FanRpm(),tsdata.GpsLatitude(),tsdata.GpsLongitude(),tsdata.GpsAltitude(),tsdata.GpsSpeed(),tsdata.LapNumber()))
        conn.commit()
        print("Dane zostały wprowadzone!")




    with amqp.Connection(conn_address) as c:
        ch = c.channel()
        ch.basic_consume(queue='test', callback=on_message, no_ack=True)
        while True:
            c.drain_events()

except Exception as e:
    print("Błąd:", e)
finally:
    cursor.close()
    conn.close()


# Create an MQTT client
#new_client = mqtt.Client()

# Set the username and password for authentication
#new_client.username_pw_set(username=username, password=password)

# Connect to the broker
#new_client.connect(broker_address, port=broker_port)

#new_client.subscribe((topic, 0))

# Define the callback function to handle incoming messages
#new_client.on_message = on_message

# Start the loop to receive messages
#new_client.loop_forever()


