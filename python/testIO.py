#!/usr/bin/python3

import IO as IO
import time

COUNT=0
LAST_TIME=0

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

def main():
	global COUNT
	global LAST_TIME

	IO.init(pins, channels)
	IO.attachInterrupt(interrupt,"CHANGE", sayHello)
	IO.clear()
	IO.enable()

	while COUNT < 256:
		CURRENT_TIME=time.time()
		if CURRENT_TIME - LAST_TIME > .1:
			IO.update(COUNT)
			COUNT+=1
			LAST_TIME=CURRENT_TIME

	IO.disable()
	IO.clear()
	IO.GPIO.cleanup()

main()

