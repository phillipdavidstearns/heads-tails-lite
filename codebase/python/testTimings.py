#!/usr/bin/python3/

from fileHandlers import *
import csv
import random
import time
import signal
import os

CHANNELS=32
channelStates=[]
eventTimes=[]
eventIndexes=[]
lastCycleTime = 0

def setLightOn(channel):
	global channelStates
	channelStates[channel] = 1

def setLightOff(channel):
	global channelStates
	channelStates[channel] = 0

def interruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	os._exit(0)

def timing():

	global eventTimes
	global eventIndexes

	for c in range(CHANNELS):
		if eventTimes[c]:
			if (time.time() > eventTimes[c][0]):
				if (eventIndexes[c][0] == 1):
					setLightOn(c)
				elif (eventIndexes[c][0] == 0):
					setLightOff(c)
				# remove the event from queue
				eventIndexes[c]=eventIndexes[c][1:]
				eventTimes[c]=eventTimes[c][1:]
				if (len(eventTimes[c])==0):
					setLightOff(c)

def generateTimings(behavior):
	times=[]
	indexes=[]
	startTime=time.time()
	offset = random.uniform(-behavior[2],behavior[2])
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

def main():

	global eventTimes
	global eventIndexes
	global channelStates
	global lastCycleTime

	for i in range(CHANNELS):
		eventTimes.append([])
		eventIndexes.append([])
		channelStates.append(0)

	behaviors = loadScore()
	behaviorList=makeBehaviorList(behaviors)

	while True:

		cycleTime = int(time.time()) % 90 
		print("--->"+str(cycleTime)+str(channelStates),end='\r')
		if( cycleTime == 0 and cycleTime != lastCycleTime):
			for c in range(CHANNELS):
				behavior = behaviors[behaviorList[c]]
				timings=generateTimings(behavior)
				eventTimes[c]+=timings[0]
				eventIndexes[c]+=timings[1]
		timing()
		lastCycleTime=cycleTime
		time.sleep(.1)

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

main()