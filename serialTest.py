#!/usr/bin/env python

#WORKS SO FAR!!!!


import serial
import RPi.GPIO as GPIO
import time
import io
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW)              #enable pin, high for send, low for receive

ser = serial.Serial(
    port='/dev/ttyAMA1',
    baudrate = 57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
i = ["<30,36,1,1>"]          #sending message  <left press, right press, auto(0)/manual(1), pump off(0)/on(1)>

GPIO.output(31, 1)
msgInterval = 3
msgTime = time.time()
while True:
    t1 = time.time()
    if t1 - msgTime >= msgInterval:
        msgTime = time.time()

        for x in i:
            ser.write(str.encode(x, encoding="ascii"))
            print(str(x))
        #GPIO.output(31, 0)

