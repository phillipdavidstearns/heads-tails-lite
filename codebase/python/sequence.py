#!/usr/bin/python3

import pigpio # using this for hardware PWM, software is not stable!!!
import signal
import time
import math
import signal
import RPi.GPIO as GPIO # using RPi.GPIO for non-PWM
import random

# GPIO pin numbers
STR = 17
DATA = 27
CLK = 22
PWM_PIN = 12
PWM_FREQ = 400 # frequency of PWM
CHANNELS = 32; # number of output channels
FPS = 30; # main refresh rate = frames per second
counter = 0
value = 0b11111111111111111111111111111111 # testing purposes


PWM = pigpio.pi()
if not PWM.connected:
	exit()

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

def keyboardInterruptHandler(signal, frame):
	print()
	print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	regClear()
	GPIO.cleanup()
	PWM.hardware_PWM(PWM_PIN, PWM_FREQ, 0)
	PWM.stop()
	exit(0)

def main():

	print("Ctrl C to quit")

	global counter
	global value

	regClear()

	while True:

		regOutput( 1 << (counter % 32) )

		if (counter % 300 == 150):
			PWM.hardware_PWM(PWM_PIN, PWM_FREQ, 1000000 )
		elif (counter % 300 == 0):
			PWM.hardware_PWM(PWM_PIN, PWM_FREQ, 100000 )

		counter += 1
		time.sleep(1)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

main()