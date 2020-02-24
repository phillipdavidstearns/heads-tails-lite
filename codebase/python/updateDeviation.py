#!/usr/bin/python3/

from fileHandlers import *
import signal
import os

def interruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	os._exit(0)

def main():

	os._exit(fetchDeviation())

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

main()