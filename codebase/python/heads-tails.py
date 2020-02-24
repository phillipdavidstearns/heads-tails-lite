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

tzOffset = -5 * 3600 # timezone offset
dotOffset = 12 # based on the start of Phase B @ 51 seconds in the cycle starting + 28 past midnight
deviation = 0
power_line_time=time.time()

behaviors=[]
channelStates=[]
eventTimes=[]
eventIndexes=[]
updateFlag=True
resynchFlag=True
refreshScoreFlag=True
headlightFlag=True

#------------------------------------------------------------------------
#	PWM
#	Used to set the brightness of the headlights
# 	***NOTE***
#	pigpiod but be running / restarted prior to running this script

PWM_PIN = 12
PWM_FREQ = 14000 # frequency of PWM

# initializes pigpio
PWM = pigpio.pi()

if not PWM.connected:
	print("pigpio faile to initialize.")
	exit()

#------------------------------------------------------------------------
#	RPi.GPIO
#	Non-PWM IO

# Shift register pings
STR = 17
DATA = 27
CLK = 22
# Interrupt pin for grid synch
GRID = 23

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

INCREMENT = 1/120.0 # each interrupt = 1/120th of a second in "grid-time"

def incrementCounter(channel):
	global power_line_time
	power_line_time += INCREMENT

#------------------------------------------------------------------------
#	HEADLIGHTS
#	updating of the actual headlight timetables is done using functions in fileHandlers.py
#		* fetchHeadlights()
#		* loadHeadlights()

# Some global variables related to headlights
headlightTimes=[ 26400, 60300 ] # default sunrise/sunset times
headlightState=0 # 0 for dim 1 for bright
lastHeadlightState=0 # 0 for dim 1 for bright
DIM = 0.15
BRIGHT = 1.0

# fetch the current date and set headlight timings accordingly
def updateHeadlightTimes():
	date=str(time.localtime()[1])+'/'+str(time.localtime()[2])
	try: # if the date is accounted for, we good
		global headlightTimes
		dim = headlights[date][0].split(':')
		bright = headlights[date][1].split(':')
		headlightTimes[0]=int(dim[0])*3600+int(dim[1])*60
		headlightTimes[1]=int(bright[0])*3600+int(bright[1])*60
	except: # otherwise we go with the defaults or last used
		pass

# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights():
	currentTime=int(adjustedTime())%86400
	if ( currentTime >= headlightTimes[0] and currentTime < headlightTimes[1] ):
		PWM.hardware_PWM(PWM_PIN, PWM_FREQ, int(DIM*1000000) ) # dim
	else:
		PWM.hardware_PWM(PWM_PIN, PWM_FREQ, int(BRIGHT*1000000) ) # bright

#------------------------------------------------------------------------
#	DEVIATION
#	
# 	* fetchDeviation()
# 	* deviationChanged()
# 	* loadDeviation()

def resynch():
	global power_line_time
	global deviation
	if fetchDeviation():
		if deviationChanged():
			deviation = loadDeviation()
			power_line_time=time.time()

#------------------------------------------------------------------------
# TIMING

# Provides a reading of time that should be synched to the grid
def adjustedTime():
	return power_line_time + tzOffset + dotOffset + deviation

#------------------------------------------------------------------------

def updateBehaviors(behaviors):
	global eventTimes
	global eventIndexes
	behaviorList=makeBehaviorList(behaviors)
	for c in range(CHANNELS):
		behavior = behaviors[behaviorList[c]]
		timings = generateTimings(behavior)
		eventTimes[c]+=timings[0]
		eventIndexes[c]+=timings[1]

def updateOutput():
	global eventTimes
	global eventIndexes
	global channelStates
	for c in range(CHANNELS):
		if eventTimes[c]:
			if (adjustedTime() > eventTimes[c][0]):
				channelStates[c]=eventIndexes[c][0]
				eventIndexes[c]=eventIndexes[c][1:]
				eventTimes[c]=eventTimes[c][1:]
				if (len(eventTimes[c])==0):
					channelStates[c]=0
	return channelStates

def generateTimings(behavior):
	times=[]
	indexes=[]
	offset = random.uniform(-behavior[2],behavior[2])
	startTime=adjustedTime()
	for t in range(len(behavior[0])):
		eventTime = startTime + offset + behavior[0][t] + random.uniform(-behavior[1][t],behavior[1][t])
		times.append(eventTime)
		if (t%2==0):
			indexes.append(1)
		else:
			indexes.append(0)
	return [times, indexes]

def makeBehaviorList(behaviors):
	behaviorList=[]
	itemCount=[0]*len(behaviors)
	while (len(behaviorList) < CHANNELS):
		candidate=random.randint(0,len(behaviors)-1)
		if (itemCount[candidate] < 2):
			itemCount[candidate] += 1
			behaviorList.append(random.randint(0,len(behaviors)-1))
	return behaviorList

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
	global eventTimes
	global eventIndexes
	global channelStates
	global behaviors

	for i in range(CHANNELS):
		eventTimes.append([])
		eventIndexes.append([])
		channelStates.append(0)

	initGPIO()
	regClear()
	fetchScore()
	behaviors = loadScore()
	resynch()
	updateHeadlightTimes()
	headlights = loadHeadlights()

def main():

	global eventTimes
	global eventIndexes
	global channelStates
	global lastCycleTime
	global power_line_time

	global updateFlag
	global resynchFlag
	global refreshScoreFlag
	global headlightFlag

	global behaviors

	while True:

		updateHeadlights()

		currentTime = int(adjustedTime())

		resynchTime = currentTime % 3600 # triggers every hour
		refreshScoreTime = currentTime  % 1800 # triggers every 1/2 hour
		refreshHeadlightTime = (currentTime - 3600) % 86400 # 86400 should trigger at ~1AM
		cycleTime = currentTime % 90

		if(refreshHeadlightTime == 0 and headlightFlag):
			updateHeadlightTimes()
			headlightFlag = False
		elif(refreshHeadlightTime != 0 and not headlightFlag):
			headlightFlag = True

		if(resynchTime == 0 and resynchFlag):
			resynch()
			resynchFlag = False
		elif(resynchTime != 0 and not resynchFlag):
			resynchFlag = True

		if(refreshScoreTime == 0 and refreshScoreFlag):
			if fetchScore():
				behaviors = loadScore()
			refreshScoreFlag = False
		elif(refreshScoreTime != 0 and not refreshScoreFlag):
			refreshScoreFlag = True

		if(cycleTime == 0 and updateFlag):
			updateBehaviors(behaviors)
			updateFlag = False
		elif(cycleTime != 0 and not updateFlag):
			updateFlag=True

		regOutput(updateOutput())

		time.sleep(1/FPS)

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

setup()
main()
