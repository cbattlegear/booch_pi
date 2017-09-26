#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime
import Adafruit_DHT
from influxdb import InfluxDBClient
import influxdb

client = InfluxDBClient(host="192.168.0.250", port=8086, database="telegraf")

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)

heaterstatus = 0
heater_switch_time = datetime.now()
heater_switch_time_change = datetime.now()

while True:
    try:
        humidity, temperature = Adafruit_DHT.read_retry(22, 3)
        temperature = (temperature*1.8)+32
        #print 'Temp: {0:0.1f} F Humidity: {1:0.1f} %'.format(temperature, humidity)
        if temperature < 76.5:    
            if not heaterstatus:
                GPIO.output(2, GPIO.LOW)
                heaterstatus = 1
                heater_switch_time_change = datetime.now()
                heater_on_time = heater_switch_time_change - heater_switch_time
                print heater_on_time
                heater_switch_time = datetime.now()
                print "Heater on"
                json_body = [
                    {
                        "measurement": "kombucha",
                        "tags": {
                            "kombucha": "environment1"
                        },
                        "fields": {
            		        "heater_status_int": heaterstatus
                        }
                    }
                ]
                try:
                    client.write_points(json_body)
                except requests.ConnectionError:
                    print "Couldn't connect to Influx"
                except influxdb.exceptions.InfluxDBClientError as content:
                    print content
                    print "Couldn't write to Influx"

        if temperature > 77.5:
            if heaterstatus:
                GPIO.output(2, GPIO.HIGH)
                heater_switch_time_change = datetime.now()
                heater_off_time = heater_switch_time_change - heater_switch_time
                print heater_off_time
                heater_switch_time = datetime.now()
                heaterstatus = 0
                print "Heater off"
                json_body = [
                    {
                        "measurement": "kombucha",
                        "tags": {
                            "kombucha": "environment1"
                        },
                        "fields": {
            		        "heater_status_int": heaterstatus
                        }
                    }
                ]
                try:
                    client.write_points(json_body)
                except requests.ConnectionError:
                    print "Couldn't connect to Influx" 
                except influxdb.exceptions.InfluxDBClientError as content:
                    print content
                    print "Couldn't write to Influx"
        heater_status_time = datetime.now() - heater_switch_time
        json_body = [
            {
                "measurement": "kombucha",
                "tags": {
                    "kombucha": "environment1"
                },
                "fields": {
                    "humidity": humidity,
    		    "temperature": temperature,
                    "heater_status_time": heater_status_time.total_seconds()
                }
            }
        ]
        try:
            client.write_points(json_body)
        except requests.ConnectionError:
            print "Couldn't connect to Influx"
        except influxdb.exceptions.InfluxDBClientError as content:
            print content
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
