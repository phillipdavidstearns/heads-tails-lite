#!/usr/bin/python3

import IO
import time
import signal

COUNT=0
FPS=30.0

# Pin assignments
strobe = 17 # latch strobe GPIO pin
data = 27 # data GPIO pin
clock = 22 # clock GPIO pin
enable = 23 # IOister enable GPIO pin
interrupt = 24 # interrupt GPIO pin

outputs = [ strobe, data, clock, enable]
inputs = [ interrupt ]
pins = [ outputs , inputs ]

channels = 8 # number of output channels

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

def main():

	global COUNT

	while True:
		IO.update(COUNT)
		COUNT+=1
		time.sleep( 1 / FPS )

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

startupIO()
main()

