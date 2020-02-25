#!/usr/bin/python3

import signal
import RPi.GPIO as GPIO # using RPi.GPIO for non-PWM

# GPIO pin numbers
STR = 17
DATA = 27
CLK = 22
CHANNELS = 8; # number of output channels
FPS = 30; # main refresh rate = frames per second
counter = 0
value = 0b11111111111111111111111111111111 # testing purposes

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

def regOutput(value):
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(DATA, value >> (CHANNELS - i - 1)  & 1)
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)
	GPIO.output(DATA, 0)

def interruptHandler(signal, frame):
	print()
	print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	regClear()
	GPIO.cleanup()
	exit(0)

def main():

	print("Ctrl C to quit")

	global counter
	global value

	regClear()

	while True:

		for i in range( CHANNELS ):
			if ( counter % ( i + 10 ) == 0 ):
				value ^= 1 << i
		regOutput( value )

		counter += 1
		time.sleep( 1 / FPS )

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

main()