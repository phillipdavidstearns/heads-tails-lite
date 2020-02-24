#!/usr/bin/python3

import RPi.GPIO as GPIO # using RPi.GPIO
import signal
import time
import os

# GPIO pin numbers
STR = 17
DATA = 27
CLK = 22
HEADLIGHTS = 12 # usually this would be pwm controlled but this 

CHANNELS = 32; # number of output channels

def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(STR, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(DATA, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(CLK, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(HEADLIGHTS, GPIO.OUT, initial=GPIO.HIGH) # make pin into an output

def regClear():
	GPIO.output(DATA, 0)
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(CLK, 1) 
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)

def allON():
	GPIO.output(DATA, 1)
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)

def keyboardInterruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	regClear()
	GPIO.cleanup()
	os._exit(0)

def main():
	allON()
	while True:
		time.sleep(1)

signal.signal(signal.SIGINT, keyboardInterruptHandler)
setup()
main()
