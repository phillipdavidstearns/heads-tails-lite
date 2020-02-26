#!/usr/bin/python3

import IO
import time
import signal

count=0
fps=30.0
channels = 8 # number of output channels

# Pin assignments

# outputs
strobe = 17 # latch strobe GPIO pin
data = 27 # data GPIO pin
clock = 22 # clock GPIO pin
enable = 23 # IOister enable GPIO pin

# inputs
interrupt = 24 # interrupt GPIO pin

# pwm
pwm_pin = 12 # pwm pin
pwm_freq = 14000
pwm_brightness = 0

# make composite lists to pass along to IO
outputs = [ strobe, data, clock, enable]
inputs = [ interrupt ]
pwm_args = [ pwm_pin, pwm_freq, pwm_brightness ]

pins = [ outputs , inputs, pwm_args ]


def sayHello(kwargs):
	print("hello!")

def interruptHandler(signal, frame):
	print()
	print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	shutdownIO()
	exit(0)

def startupIO():
	IO.init(pins, channels)
	IO.attachInterrupt(interrupt,"CHANGE", sayHello)
	IO.clear()
	IO.enable()

def shutdownIO():
	IO.disable()
	IO.clear()
	IO.cleanup()

def boolean_list(value):
	booleans=[]
	for i in range(0,32):
		booleans+= value >> i & 1
	return booleans

def main():

	global count

	while True:
		IO.update(boolean_list(count))
		count+=1
		if (count % 300 == 150):
			IO.setPWM(1.0)
		elif (count % 300 == 0):
			IO.setPWM(0.1)
		time.sleep( 1 / fps )

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

startupIO()
main()

