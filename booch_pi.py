#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime
import Adafruit_DHT
from influxdb import InfluxDBClient
import influxdb
import sys
import os

import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# Setup for Azure IotHub
iothub_connection_string = os.environ.get('IOTHUB_CONN_STRING')
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000
AVG_WIND_SPEED = 10.0
SEND_CALLBACKS = 0

def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    map_properties = message.properties()
    print ( "    message_id: %s" % message.message_id )
    print ( "    correlation_id: %s" % message.correlation_id )
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )

def iothub_client_init():
    # prepare iothub client
    client = IoTHubClient(iothub_connection_string, PROTOCOL)
    # set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    client.set_option("logtrace", 0)
    return client

# Setup for Influx client
influx_client = InfluxDBClient(host="192.168.0.250", port=8086, database="telegraf")

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)

heaterstatus = 0
heater_switch_time = datetime.now()
heater_switch_time_change = datetime.now()

iothub_client = iothub_client_init()
message_counter = 0

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
                json_body_influx = [
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
                json_body_iothub = {
                    "deviceId": "booch_pi",
            		"heater_status_int": heaterstatus
                }

                iothub_message = IoTHubMessage(bytearray(str(json_body_iothub), 'utf8'))
                iothub_message.message_id = "message_%d" % message_counter
                iothub_message.correlation_id = "correlation_%d" % message_counter
                
                try:
                    iothub_client.send_event_async(iothub_message, send_confirmation_callback, message_counter)
                    status = iothub_client.get_send_status()
                    print ( "Send status: %s" % status )
                    message_counter += 1

                    influx_client.write_points(json_body_influx)
                except requests.ConnectionError:
                    print "Couldn't connect to Influx"
                except influxdb.exceptions.InfluxDBClientError as content:
                    print content
                    print "Couldn't write to Influx"
                except IoTHubError as iothub_error:
                    print ( "Unexpected error %s from IoTHub" % iothub_error )

        if temperature > 77.5:
            if heaterstatus:
                GPIO.output(2, GPIO.HIGH)
                heater_switch_time_change = datetime.now()
                heater_off_time = heater_switch_time_change - heater_switch_time
                print heater_off_time
                heater_switch_time = datetime.now()
                heaterstatus = 0
                print "Heater off"
                json_body_influx = [
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
                json_body_iothub = {
                    "deviceId": "booch_pi",
            		"heater_status_int": heaterstatus
                }

                iothub_message = IoTHubMessage(bytearray(str(json_body_iothub), 'utf8'))
                iothub_message.message_id = "message_%d" % message_counter
                iothub_message.correlation_id = "correlation_%d" % message_counter
                
                try:
                    iothub_client.send_event_async(iothub_message, send_confirmation_callback, message_counter)
                    status = iothub_client.get_send_status()
                    print ( "Send status: %s" % status )
                    message_counter += 1

                    influx_client.write_points(json_body_influx)
                except requests.ConnectionError:
                    print "Couldn't connect to Influx" 
                except influxdb.exceptions.InfluxDBClientError as content:
                    print content
                    print "Couldn't write to Influx"
                except IoTHubError as iothub_error:
                    print ( "Unexpected error %s from IoTHub" % iothub_error )

        heater_status_time = datetime.now() - heater_switch_time
        json_body_influx = [
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
        json_body_iothub = {
            "deviceId": "booch_pi",
            "humidity": humidity,
    		"temperature": temperature,
            "heater_status_time": heater_status_time.total_seconds()
        }
        iothub_message = IoTHubMessage(bytearray(str(json_body_iothub), 'utf8'))
        iothub_message.message_id = "message_%d" % message_counter
        iothub_message.correlation_id = "correlation_%d" % message_counter
        
        try:
            iothub_client.send_event_async(iothub_message, send_confirmation_callback, message_counter)
            status = iothub_client.get_send_status()
            print ( "Send status: %s" % status )
            message_counter += 1

            influx_client.write_points(json_body_influx)
        except requests.ConnectionError:
            print "Couldn't connect to Influx"
        except influxdb.exceptions.InfluxDBClientError as content:
            print content
            print "Couldn't write to Influx"
        except IoTHubError as iothub_error:
            print ( "Unexpected error %s from IoTHub" % iothub_error )
        time.sleep(10)
    except KeyboardInterrupt:
        print " Killing process"
        GPIO.cleanup()
        break
    except:    
        print "Something fucked up"
        print "Unexpected error:", sys.exc_info()[0]
