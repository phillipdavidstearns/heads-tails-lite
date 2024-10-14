# Heads Tails Lite Assembly Guide

* Parts Included
* Connections

## Parts

### 10x10 (x3)

* 150W 12V DC Power Supply
* Raspberry Pi Zero W
* 5V 2.5A Power Supply for the Raspberry Pi Zero W
* 3x LED Driver boards
* 1x Shift Register board
* Female header board jumpers for interconnection
* 1x2 120VAC power splitter
* 1x IEC power cable

### 20x10 (x1)

* 350W 12V DC Power Supply
* Raspberry Pi Zero W
* 5V 2.5A Power Supply for the Raspberry Pi Zero W
* 6x LED Driver boards
* 1x Shift Register board
* Female header board jumpers for interconnection
* * 1x2 120VAC power splitter
* 1x IEC power cable

## Connections

These instructions apply to the 20x10 and 10x10 configurations. The key difference is that the headlight PWM connection is split on one of the LED Driver boards.

### Order of Connections

Start with all power supplies disconnected from 110-240VAC.

* Wire up the 12V DC power supply with an appropriate cable to supply 110-240AC.

1. Secure boards to the project housing or a rigid backing material.
	* [Remove the housing for the Raspberry Pi Zero W](./pi_housing.png)
1. Connect Raspberry Pi Zero W to the Shift Register board. [Refer to the connection diagram photoshop diagrams](./20x10_connection_diagram.psd). Pins are indicated and labelled using layer names. Sections are grouped and visibility can be toggled for clarity.
	* GND
	* +5V
	* STROBE
	* DATA
	* CLOCK
	* ENABLE
	* Headlight PWM
		* *note: this connection is made between the Raspberry Pi Zero W and the LED Driver board. Subsequent connections are daisy chained as illustrated in the guide.*

1. Connect the **taillights** and **headlights** to the **green screw terminal blocks**.
1. Connect the **shift register boards** to the **LED driver boards** using the female header jumper wires provided.
	* The shift register pin order does not matter since the code randomly maps behaviors to different channels.
	* If strict adherence to the pin order is desired, the register outputs are indicated in the psd. A datasheet is also provided [here](./CD4094.pdf).
1. Connect the **ground bus terminals** on the **LED driver boards** to the **ground bus terminals** on the **shift register board**. *note: DO NOT daisy chain the ground connections.
1. Connect the ground terminal of the 12V DC power supply to the **ground bus terminal** on the **shift register board**.
1. Connect the MicroUSB power connector to the Raspberry Pi Zero W's right most USB input.
1. Connect the 12 power supply and Raspberry Pi Zero W power supply to the provided splitter.
1. Prior to connecting to VAC, test that 12V and 5V power contacts do no short to ground.
1. Connect power and enjoy the show.