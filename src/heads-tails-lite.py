#!/usr/bin/python3

#------------------------------------------------------------------------
# heads-tails-lite.py
#
# Refactoring of heads-tails.py

from fileHandlers import loadScore
import IO
import signal
import os
import random
import time
from datetime import datetime, UTC, timedelta
import argparse
import logging

#------------------------------------------------------------------------
# HEADLIGHTS
# Some global variables related to headlights
headlightTimes = [ 25200, 68400 ] # default sunrise/sunset times of 7am 7pm
headlightState = 0 # 0 for dim 1 for bright
DIM = 0.25
BRIGHT = 1.0

# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights():
  timedelta = datetime.now(UTC).replace(tzinfo=None) - datetime.now()
  difference = timedelta.seconds + timedelta.microseconds * 0.000001
  currentTime = adjustedTime() % 86400 - difference
  if ( currentTime >= headlightTimes[0] and currentTime < headlightTimes[1] ):
    IO.setPWM(DIM)
  else:
    IO.setPWM(BRIGHT)

#------------------------------------------------------------------------
# TIMING

# Provides a reading of time that should be synched to the grid
def adjustedTime():
  return datetime.now().timestamp()

#------------------------------------------------------------------------

def updateEvents():
  global eventTimes
  global eventStates
  eventList = makeEventList()
  for c in range(channels):
    logging.debug("================================================================")
    times, states = generateTimings(behaviors[eventList[c]])
    logging.debug(f"eventTimes[{c}]: {eventTimes[c]}\neventStates[{c}]: {eventStates[c]}")
    eventTimes[c] += times
    eventStates[c] += states
    logging.debug(f"updateEvents():\neventTimes[{c}]: {repr(eventTimes[c])}\neventStates[{c}]: {repr(eventStates[c])}")

#------------------------------------------------------------------------

def updateChannels():
  global eventTimes
  global eventStates
  global channelStates
  for c in range(channels):
    if eventTimes[c]:
      if (adjustedTime() >= eventTimes[c][0]):
        channelStates[c] = eventStates[c][0]
        eventStates[c] = eventStates[c][1:] # remove from queue
        eventTimes[c] = eventTimes[c][1:] # remove from queue
        if (len(eventTimes[c]) == 0):
          channelStates[c] = 0

  logging.debug(f"channelStates: {repr(channelStates)}")

  return channelStates

#------------------------------------------------------------------------

def generateTimings(behavior):
  times = []
  states = []
  offset = random.uniform(-behavior[2], behavior[2])
  startTime = adjustedTime()

  for t in range(len(behavior[0])):
    eventTime = startTime + offset + behavior[0][t] + random.uniform(-behavior[1][t], behavior[1][t])
    times.append(eventTime)
    if (t % 2 == 0):
      states.append(1)
    else:
      states.append(0)

  logging.debug(f"generateTimings():\nbehavior: {repr(behavior)}\ntimes: {repr(times)}\nstates: {repr(states)}")

  return times, states

#------------------------------------------------------------------------

def makeEventList():
  eventList = []
  itemCount = [0] * len(behaviors)

  while (len(eventList) < channels):
    candidate = random.randint(0, len(behaviors) - 1)
    if (itemCount[candidate] < max_repeat):
      eventList.append(candidate)
      itemCount[candidate] += 1

  logging.debug(f"makeEventList() - eventList: {repr(eventList)}")

  return eventList

#----------------------------------------------------------------

def interruptHandler(signal, frame):
  logging.info(f"interruptHandler - caught signal: {signal}, frame: {frame}")
  shutdownIO()
  os._exit(0)

#----------------------------------------------------------------

def startupIO():
  logging.info(f"Starting up IO")

  # outputs
  strobe = 17 # latch strobe GPIO pin
  data = 27 # data GPIO pin
  clock = 22 # clock GPIO pin
  enable = 23 # IOister enable GPIO pin

  # pwm
  pwm_pin = 12 # pwm pin
  pwm_freq = 10000
  pwm_brightness = 0

  # make composite lists to pass along to IO
  outputs = [ strobe, data, clock, enable ]
  inputs = []
  pwm_args = [ pwm_pin, pwm_freq, pwm_brightness ]

  pins = [ outputs , inputs, pwm_args ]

  IO.init(pins, channels)
  IO.clear()
  IO.enable()

#----------------------------------------------------------------

def shutdownIO():
  logging.info(f"Shutting down IO")
  IO.disable()
  IO.clear()
  IO.cleanup()

#----------------------------------------------------------------

def main():

  updateFlag = True

  while True:

    updateHeadlights()

    cycleTime = int(adjustedTime()) % 90
    if(cycleTime == 0 and updateFlag):
      updateEvents()
      updateFlag = False
    elif(cycleTime != 0 and not updateFlag):
      updateFlag = True

    IO.update(updateChannels())
    time.sleep(1 / fps)

#----------------------------------------------------------------

if __name__ == "__main__":
  signal.signal(signal.SIGINT, interruptHandler)
  signal.signal(signal.SIGTERM, interruptHandler)
  signal.signal(signal.SIGHUP, interruptHandler)

  parser = argparse.ArgumentParser(description='heads-tails-lite')

  # create arguments
  parser.add_argument(
    '-l',
    dest='log_level',
    default=10,
    choices=[0, 10, 20, 30, 40, 50],
    type=int,
    help='log levels: 0=NOTSET 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL'
  )

  # parse the args
  args = parser.parse_args()

  logging.basicConfig(
    level=args.log_level,
    format='[HEADS-TAILS-LITE] - %(levelname)s | %(message)s'
  )

  max_repeat = 3
  fps = 30.0
  channels = 32 # number of output channels

  try:
    startupIO()
  except Exception as e:
    logging.error(f"Failed to start up IO: {repr(e)}")
    os._exit(0)

  eventTimes = [[]] * channels
  eventStates = [[]] * channels
  channelStates = [0] * channels

  try:
    behaviors = loadScore()
  except Exception as e:
    logging.error(f"Failed to load behaviors from loadScore: {repr(e)}")
    os._exit(0)

  updateEvents()

  try:
    main()
  except Exception as e:
    logging.error(f"While executing main(): {repr(e)}")
  finally:
    os._exit(0)
