#! /usr/bin/python3

import sys
from PyQt5 import QtWidgets, uic, QtCore
from SerialArduinoIO import *

app = QtWidgets.QApplication(sys.argv)
serialComm = SerialArduinoIO()
# print("initializing")
sleep(5)
threads = []
change = 0


#########################################################
##                  FUNCTIONS                          ##
#########################################################

# this set of functions increases or decreases the pressures by 5 and sends the msg via serial.
# pressure limit is 5-90 psi


def leftI(self):
    global change
    window.leftDisp.display(serialComm.leftPress_s)

    if serialComm.lss < 85:
        serialComm.lss += 5

    else:
        serialComm.lss = 90

    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)
    change = 1


def leftD(self):
    global change
    if serialComm.lss > 10:
        serialComm.lss -= 5

    else:
        serialComm.lss = 5
    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)
    change = 1


def rtI(self):
    global change
    if serialComm.rss < 85:
        serialComm.rss += 5

    else:
        serialComm.rss = 90
    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)
    change = 2


def rtD(self):
    global change
    if serialComm.rss > 10:
        serialComm.rss -= 5

    else:
        serialComm.rss = 5
    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)
    change = 2


# this set of functions changes between auto and manual mode
# and turns the pump on and off in manual mode.
# the pump should automatically turn off in auto if it was on

def autoMode(self):
    serialComm.ms = 0
    serialComm.ps = 0
    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)


def manMode(self):
    serialComm.ms = 1
    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)


def pumpOnOff(self):
    if serialComm.mode_s == 1:
        if serialComm.pump_s == 1:
            serialComm.ps = 0
        elif serialComm.pump_s == 0:
            serialComm.ps = 1
    message = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
    serialComm.sendMessage(message)


# displays pressure on the screen.  needs to show setting values when buttons are pressed
def display():
    global change
    while True:
        if change == 1:
            window.leftDisp.display(serialComm.lss)
            change = 0
            sleep(1)

        if change == 2:
            window.rightDisp.display(serialComm.rss)
            change = 0
            sleep(1)

        window.leftDisp.display(serialComm.leftPress_s)
        window.rightDisp.display(serialComm.rtPress_s)
        '''
        if 5 > serialComm.leftPress_s or serialComm.leftPress_s > 90:
            window.leftDisp.setStyleSheet("background-color: rgb(255,0,0)")
        else:
            window.leftDisp.setStyleSheet("")

        if 5 > serialComm.rtPress_s or serialComm.rtPress_s > 90:
            window.rightDisp.setStyleSheet("background-color: rgb(255,0,0)")
        else:
            window.rightDisp.setStyleSheet("")

        sleep(0.2)
        '''


# turns the increase, decrease, and pump buttons green when the components are energized
def turnButtonGreen(posit):
    if posit == 0:
        window.leftInc.setStyleSheet("background-color: rgb(0,255,0)")
    elif posit == 1:
        window.leftDec.setStyleSheet("background-color: rgb(0,255,0)")
    elif posit == 2:
        window.rtInc.setStyleSheet("background-color: rgb(0,255,0)")
    elif posit == 3:
        window.rtDec.setStyleSheet("background-color: rgb(0,255,0)")
    elif posit == 4:
        window.pumpCont.setStyleSheet("background-color: rgb(0,255,0)")


# resets button colors after relays deenergize
def resetButtonColor(posit):
    if posit == 0:
        window.leftInc.setStyleSheet("")
    elif posit == 1:
        window.leftDec.setStyleSheet("")
    elif posit == 2:
        window.rtInc.setStyleSheet("")
    elif posit == 3:
        window.rtDec.setStyleSheet("")
    elif posit == 4:
        window.pumpCont.setStyleSheet("")


# checks if the message to the arduino has been sent and received.
# may want an indication to show up on the screen during a miscompare
def compare():
    while True:
        if serialComm.ms == 1:
            rpiMsg = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.ps}>"
            ardMsg = f"<{serialComm.leftSetting_s}, {serialComm.rtSetting_s}, {serialComm.mode_s}, {serialComm.pump_s}>"
            if rpiMsg != ardMsg:
                serialComm.sendMessage(rpiMsg)
                print("sending: ", rpiMsg)
                print("receiving: ", ardMsg)
                window.label.setText("W o r k i n g")

        # doesn't matter what the pump status is in auto mode
        elif serialComm.ms == 0:
            rpiMsg = f"<{serialComm.lss}, {serialComm.rss}, {serialComm.ms}, {serialComm.pump_s}>"
            ardMsg = f"<{serialComm.leftSetting_s}, {serialComm.rtSetting_s}, {serialComm.mode_s}, {serialComm.pump_s}>"

            if rpiMsg != ardMsg:
                serialComm.sendMessage(rpiMsg)
                print("sending: ", rpiMsg)
                print("receiving: ", ardMsg)
                window.label.setText("W o r k i n g")

        sleep(0.5)
        window.label.setText("")
################################################
##             THE PROGRAM                    ##
################################################


window = uic.loadUi("airbagControl.ui")

# SIGNAL CONNECTIONS
window.leftDec.clicked.connect(leftD)
window.leftInc.clicked.connect(leftI)
window.rtDec.clicked.connect(rtD)
window.rtInc.clicked.connect(rtI)
window.autoSel.clicked.connect(autoMode)
window.manSel.clicked.connect(manMode)
window.pumpCont.clicked.connect(pumpOnOff)
serialComm.energized.connect(turnButtonGreen)
serialComm.deenergized.connect(resetButtonColor)
'''
if serialComm.mode_s == 1:
    window.autoSel.setChecked(True)
else:
    window.manSel.setChecked(True)
'''
# THREADS
threading.Thread(target=serialComm.receiveData, daemon=True).start()
threading.Thread(target=display, daemon=True).start()
threading.Thread(target=compare, daemon=True).start()

window.show()
app.exec()
