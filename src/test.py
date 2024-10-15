#!/usr/bin/python3

#------------------------------------------------------------------------

import IO
import signal
import os
from random import randint
import time
from math import sin, pow, pi
import logging

#------------------------------------------------------------------------

channels = 32 # number of output channels

#------------------------------------------------------------------------
#	HEADLIGHTS

# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights(angle):
	brightness = pow(sin(2 * pi * angle), 2)
	logging.debug(f"Setting headlight brightness to: {str(brightness)}")
	IO.setPWM(brightness) # dim

def updateChannels(channel):
	channelStates = [0] * channels
	channelStates[channel] = 1
	logging.debug(f"Updating channels: {repr(channelStates)}")
	return channelStates

#------------------------------------------------------------------------

def interruptHandler(signal, frame):
	shutdownIO()
	os._exit(0)

def setup():
	startupIO()

def startupIO():
	# outputs
	strobe = 17 # latch strobe GPIO pin
	data = 27 # data GPIO pin
	clock = 22 # clock GPIO pin
	enable = 23 # IOister enable GPIO pin

	# pwm
	pwm_pin = 12 # pwm pin
	pwm_freq = 14000
	pwm_brightness = 0

	# make composite lists to pass along to IO
	outputs = [ strobe, data, clock, enable]
	inputs = [ ]
	pwm_args = [ pwm_pin, pwm_freq, pwm_brightness ]

	pins = [ outputs , inputs, pwm_args ]
	IO.init(pins, channels)
	IO.clear()
	IO.enable()

def shutdownIO():
	IO.disable()
	IO.clear()
	IO.cleanup()

def main():
	fps = 1.0
	frameCount = 0
	rate = 0.01
	angle = 0

	while True:
		
		try:
			IO.update(updateChannels(frameCount))
		except Exception as e:
			logging.warning(f"Unable to update IO: {repr(e)}")

		frameCount += 1
		frameCount %= channels

		try:
			updateHeadlights(angle)
		except Exception as e:
			logging.warning(f"Unable to update headlight brightness: {repr(e)}")

		angle += rate
		angle %= 1

		time.sleep( 1 / fps )


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)
	signal.signal(signal.SIGTERM, interruptHandler)
	signal.signal(signal.SIGHUP, interruptHandler)

	logging.basicConfig(
	  level=0,
	  format='[HEADS-TAILS-TEST] - %(levelname)s | %(message)s'
	)

	try:
		setup()
	except Exception as e:
		logging.error(f"Failed to complete setup(): {repr(e)}")
		os._exit(0)

	try:
		main()
	except Exception as e:
		logging.error(f"While executing main(): {repr(e)}")
	finally:
		os._exit(0)