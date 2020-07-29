#!/usr/bin/env python

# works!  check the ground!!

# also collaborate inputs into outgoing data
# currently takes properly formatted string as input
# this will end up being the backend for the airbag control system

import threading
import serial
import RPi.GPIO as GPIO
import time
import io
import PyQt5
from time import sleep

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal


class SerialArduinoIO(QObject):
    energized = pyqtSignal(int)
    deenergized = pyqtSignal(int)
    man_or_auto_mode = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bad_chars = '<>'
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW)              # enable pin, high for send, low for receive

        # holds statuses for system components

        self.ps = 0         # pump status
        self.lfs = 0        # left fill status
        self.rfs = 0        # right fill status
        self.lds = 0        # left dump status
        self.rds = 0        # right dump status
        self.lss = 0        # left setting status
        self.rss = 0        # right setting status
        self.lps = 0        # left pressure status
        self.rps = 0        # right pressure status
        self.ms = 0         # mode status

        self.pump_s = 46
        self.leftFill_s = 46
        self.rtFill_s = 46
        self.leftDump_s = 46
        self.rtDump_s = 46
        self.leftSetting_s = 46
        self.rtSetting_s = 46
        self.leftPress_s = 46
        self.rtPress_s = 46
        self.mode_s = 46

        self.counter = 0

        self.ser = serial.Serial(
            port='/dev/ttyAMA1',
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        # threading.Thread(target=self.receiveData, daemon=True).start()

    # sends the message to arduino.  must be in proper format
    # <left press, right press, auto(0)/manual(1), pump off(0)/on(1)>
    def sendMessage(self, msg):
        GPIO.output(31, 1)
        sleep(.1)
        for m in msg:
            self.ser.write(str.encode(m, encoding="ascii"))

        sleep(.1)
        GPIO.output(31, 0)
        print(msg)

    def receiveData(self):
        while True:
            if self.ser.in_waiting > 0:

                try:
                    line = self.ser.readline()           # byte object
                    d_line = line.decode("ascii")   # str object
                    for c in self.bad_chars:
                        d_line = d_line.replace(c, "")

                    status = [int(x) for x in d_line.split(',') if x.strip().isdigit()]
                    print(status)                 # debugging
                    self.pump_s = status[0]
                    self.leftFill_s = status[1]
                    self.rtFill_s = status[2]
                    self.leftDump_s = status[3]
                    self.rtDump_s = status[4]
                    self.leftSetting_s = status[5]
                    self.rtSetting_s = status[6]
                    self.leftPress_s = status[7]
                    self.rtPress_s = status[8]
                    self.mode_s = status[9]

                    # 5 tries to populate data
                    if self.counter < 5:
                        self.populateLocalVariables()
                        self.counter += 1
                    self.statusUpdateSignals()

                except Exception as e:
                    print(e)
                    pass

    def populateLocalVariables(self):
        self.ps = self.pump_s  # pump status
        self.lfs = self.leftFill_s  # left fill status
        self.rfs = self.rtFill_s  # right fill status
        self.lds = self.leftDump_s  # left dump status
        self.rds = self.rtDump_s  # right dump status
        self.lss = self.leftSetting_s  # left setting status
        self.rss = self.rtSetting_s  # right setting status
        self.lps = self.leftPress_s  # left pressure status
        self.rps = self.rtPress_s  # right pressure status
        self.ms = self.mode_s  # mode status

    def statusUpdateSignals(self):
        if self.leftFill_s == 1:
            self.energized.emit(0)
        else:
            self.deenergized.emit(0)

        if self.leftDump_s == 1:
            self.energized.emit(1)
        else:
            self.deenergized.emit(1)

        if self.rtFill_s == 1:
            self.energized.emit(2)
        else:
            self.deenergized.emit(2)

        if self.rtDump_s == 1:
            self.energized.emit(3)
        else:
            self.deenergized.emit(3)

        if self.pump_s == 1:
            self.energized.emit(4)
        else:
            self.deenergized.emit(4)

        if self.mode_s == 0:
            self.man_or_auto_mode.emit(0)
        else:
            self.man_or_auto_mode.emit(1)
