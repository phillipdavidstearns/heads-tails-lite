#!/usr/bin/python3

from fileHandlers import *
import signal
import os
import pigpio # using this for hardware PWM, software is not stable!!!
import RPi.GPIO as GPIO # using RPi.GPIO for non-PWM
import random
import time

#------------------------------------------------------------------------

CHANNELS=32
FPS = 30

INCREMENT = 1/120.0

tzOffset = -5 * 3600
dotOffset = 0 # based on the start of Phase B @ 51 seconds in the cycle starting + 28 past midnight
deviation = 0
power_line_time=time.time()

channelStates=[]
eventTimes=[]
eventIndexes=[]
lastCycleTime = 0

script_dir = os.path.split(os.path.realpath(__file__))[0]

STR = 17
DATA = 27
CLK = 22
GRID = 23

PWM_PIN = 12
PWM_FREQ = 14000 # frequency of PWM

PWM = pigpio.pi()

if not PWM.connected:
	exit()

def adjustedTime():
	return power_line_time + tzOffset + dotOffset + deviation

#------------------------------------------------------------------------
# RPi.GPIO

def initGPIO():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(STR, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(DATA, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(CLK, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
	GPIO.setup(GRID, GPIO.IN) # make pin into an input
	GPIO.add_event_detect(GRID, GPIO.BOTH, callback=incrementCounter)

def regClear():
	GPIO.output(DATA, 0)
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)

def regOutput(channels):
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(DATA, channels[CHANNELS - i - 1])
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)
	GPIO.output(DATA, 0)

def incrementCounter(channel):
	global power_line_time
	power_line_time += INCREMENT

def resynch():
	global power_line_time
	global deviation
	fetchDeviation()
	deviation = loadDeviation()
	power_line_time=time.time()

#------------------------------------------------------------------------

def interruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	regClear()
	GPIO.cleanup()
	PWM.hardware_PWM(PWM_PIN, PWM_FREQ, 0)
	PWM.stop()
	os._exit(0)

def setup():
	initGPIO()
	resynch()

def main():

	while True:
		print(" plt: "+str(power_line_time)+", adj: "+str(adjustedTime())+", local: "+str(time.time()),end='\r')
		time.sleep(1/FPS)

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

setup()
main()