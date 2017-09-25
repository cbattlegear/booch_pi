#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.0.250", port=8086, database="telegraf")

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)

heaterstatus = False

while True:
    try:
        humidity, temperature = Adafruit_DHT.read_retry(22, 3)
        temperature = (temperature*1.8)+32
        print 'Temp: {0:0.1f} F Humidity: {1:0.1f} %'.format(temperature, humidity)
        if temperature < 76.5:    
            if not heaterstatus:
                GPIO.output(2, GPIO.LOW)
                heaterstatus = True
                print "Heater on"
        if temperature > 77.5:
            if heaterstatus:
                GPIO.output(2, GPIO.HIGH)
                heaterstatus = False
                print "Heater off"
        json_body = [
            {
                "measurement": "kombucha",
                "tags": {
                    "kombucha": "environment1"
                },
                "fields": {
                    "humidity": humidity,
    		        "temperature": temperature,
    		        "heater_status": heaterstatus
                }
            }
        ]
        try:
            client.write_points(json_body)
        except ConnectionError:
            print "Couldn't write to Influx"
        time.sleep(10)
    except KeyboardInterrupt:
        print " Killing process"
        GPIO.cleanup()
        break
    except:
        print "Something fucked up"
        GPIO.cleanup()
        break
