#!/usr/bin/python3

import RPi.GPIO as GPIO # using RPi.GPIO

# GPIO pin numbers
STR = 17
DATA = 27
CLK = 22

CHANNELS = 32; # number of output channels

def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(STR, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(DATA, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(CLK, GPIO.OUT, initial=GPIO.LOW) # make pin into an output

def regClear():
	GPIO.output(DATA, 0)
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)

def main():
	regClear()
	GPIO.cleanup()

setup()
main()
