# -*- coding:utf-8 -*-
import threading, time
from queue import Queue
import RPi.GPIO as GPIO


#GPIO define
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13

KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

class keyboardThread(threading.Thread):
    def __init__(self, que, kill):
        threading.Thread.__init__(self)
        self.que = que
        self.kill = kill

    def run(self):
        while self.kill.empty():
            if not GPIO.input(KEY1_PIN):
                self.que.put(0)
                time.sleep(0.5)
            if not GPIO.input(KEY2_PIN):
                self.que.put(1)
                time.sleep(0.5)
            if not GPIO.input(KEY3_PIN):
                self.que.put(2)
                time.sleep(0.5)


thread, kill = None, Queue(5)

def Init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
    GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
    GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
    GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
    GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
    GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
    GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
    GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

    global thread, kill
    que = Queue(100)
    while not kill.empty(): kill.get()
    thread = keyboardThread(que, kill)
    thread.start()

    return que

def clear():
    global thread, kill
    if thread is not None:
        kill.put(0)
        thread.join()
        GPIO.cleanup()