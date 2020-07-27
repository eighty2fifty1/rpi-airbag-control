#!/usr/bin/env python

#works!  check the ground!!

#also collaborate inputs into outgoing data
#currently takes properly formatted string as input
#this will end up being the backend for the airbag control system


import serial
import RPi.GPIO as GPIO
import time
import io
import binascii
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW)              #enable pin, high for send, low for receive

#holds statuses for system components
pump_s = 0
leftFill_s = 0
rtFill_s = 0
leftDump_s = 0
rtDump_s = 0
leftSetting_s = 0
rtSetting_s = 0
leftPress_s = 0
rtPress_s = 0
mode_s = 0

def sendMessage(message):
    GPIO.output(31,1)
    sleep(.1)
    for m in message:
        ser.write(str.encode(m, encoding="ascii"))

    sleep(.1)
    GPIO.output(31, 0)
    print(message)

ser = serial.Serial(
    port='/dev/ttyAMA1',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


bad_chars = '<>'
msgInterval = 3
msgTime = time.time()
while True:
    sendMessage(input("Enter left press, right press, manual mode, and pump command"))  # sending message  <left press, right press, auto(0)/manual(1), pump off(0)/on(1)>

    '''
    t1 = time.time()
    if t1 - msgTime >= msgInterval:
        GPIO.output(31, 1)
        sleep(.1)
        msgTime = time.time()

        for x in i:
            ser.write(str.encode(x, encoding="ascii"))
            print(str(x))
        sleep(.1)
        GPIO.output(31, 0)
    '''
    if(ser.in_waiting > 0):

        try:
            line = ser.readline()           #byte object
            d_line = line.decode("ascii")   #str object
            for c in bad_chars:
                d_line = d_line.replace(c, "")

            status = [int(x) for x in d_line.split(',') if x.strip().isdigit()]
            pump_s = status[0]
            leftFill_s = status[1]
            rtFill_s = status[2]
            leftDump_s = status[3]
            rtDump_s = status[4]
            leftSetting_s = status[5]
            rtSetting_s = status[6]
            leftPress_s = status[7]
            rtPress_s = status[8]
            mode_s = status[9]
        except Exception as e:
            print(e)
            pass
