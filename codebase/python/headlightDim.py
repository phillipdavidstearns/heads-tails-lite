#!/usr/bin/python3

# import pigpio # using this for hardware PWM, software is not stable!!!
import time
import signal
import pigpio
	import argparse

	parser = argparse.ArgumentParser(description='Set brightness of headlights')
	parser.add_argument('-b', type=float, default=0.15, help='brightness %')

	args = parser.parse_args()

# GPIO pin numbers

PWM_PIN = 12
PWM_FREQ = 14000 # frequency of PWM
CHANNELS = 32; # number of output channels
BRIGHT=int(args.b*1000000)
FPS=30.0
PWM = pigpio.pi()
if not PWM.connected:
	exit()

PWM.hardware_PWM(PWM_PIN, PWM_FREQ, BRIGHT)


def interruptHandler(signal, frame):
	print()
	print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	PWM.hardware_PWM(PWM_PIN, PWM_FREQ, 0)
	PWM.stop()
	exit(0)

def main():

	while True:
		# theTime=int(time.time())
		# if (theTime % 2 == 1):
		# 	PWM.hardware_PWM(PWM_PIN, PWM_FREQ, BRIGHT )
		# else:
		# 	PWM.hardware_PWM(PWM_PIN, PWM_FREQ, DIM )
		time.sleep( 1/FPS )


signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

main()
