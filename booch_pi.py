#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT


GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)
while True:

try:
    GPIO.output(2, GPIO.LOW)
    time.sleep(10)
except KeyboardInterrupt:
    print"Quit"
    GPIO.cleanup()
