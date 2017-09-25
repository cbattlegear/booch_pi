#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(22, 4)
    print 'Temp: {0:0.1f} C Humidity: {1:0.1f} %'.format(temperature, humidity)
    if temperature < 76.5:    
        try:
            GPIO.output(2, GPIO.LOW)
            time.sleep(10)
        except:
            print "Failed to turn on Relay"
    if temperature > 77.5:
        try:
            GPIO.output(2, GPIO.HIGH)
            time.sleep(10)
        except:
            print "Failed to turn off Relay"
    
GPIO.cleanup()
