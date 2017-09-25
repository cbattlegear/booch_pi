#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(22, 3)
    temperature = (temperature*1.8)+32
    print 'Temp: {0:0.1f} F Humidity: {1:0.1f} %'.format(temperature, humidity)
    try:
        if temperature < 76.5:    
            GPIO.output(2, GPIO.LOW)
            time.sleep(10)
        if temperature > 77.5:
            GPIO.output(2, GPIO.HIGH)
            time.sleep(10)
    except KeyboardInterrupt:
        print " Killing process"
        GPIO.cleanup()
