# Heads Tails Lite

A piece by Madeline Hollander. Software and Electronics by Phillip David Stearns.

## Codebase Overview

Python code to run lighting control on a Raspberry Pi is in the `src` directory:

* Main script: `heads-tails-lite.py`
* GPIO helper script: `IO.py`
* File loading script: `fileHandlers.py`
* Test routine: `test.py`

## Dependencies

<a id="hardware"></a>
### Hardware

* Intended device: **Raspberry Pi Zero W v1.1**
* Tested on Raspberry Pi 3 B+, 4 B, Zero W

NOTE: You will need to purchase a full Raspberry Pi Zero W kit. This should also work on a Raspberry Pi Zero 2w, but it has not been tested.

### Software

* python3 (should come pre-installed on Raspberry Pi): `sudo apt-get install python3`
* [pigpio python](http://abyz.me.uk/rpi/pigpio/python.html): `sudo apt-get install python3-pigpio pigpiod`
* RPi.GPIO (should come pre-installed on Raspberry Pi): `sudo apt-get install python3-rpi.gpio`

## Installation

Updated October 14th, 2024. Instructions based on Mac OSX 14.3.1

### Install [`homebrew`](https://brew.sh/)

1. Open terminal:
	1. press `command+spacebar`
	2. Type `terminal`
	3. Press `return`
1. Copy + paste into terminal: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
1. Press `return`
1. Follow any instructions from the command line

### Install [Raspberry Pi Imager](https://formulae.brew.sh/cask/raspberry-pi-imager#default):

1. Copy and past into terminal: `brew install --cask raspberry-pi-imager`
1. Press `return`

### Flash RspiOS onto a MicroSD Card

1. Insert the MicroSD card (provided in kit) into the card adapter (also provided with kit).
1. Insert card into appropriate port.
1. Click **Allow** if prompted by the OS.

#### Raspberry Pi Imager:

1. Press `command+spacebar`
1. Type `Raspberry Pi Imager`
1. Press `return`
1. Click **CHOOSE DEVICE**
1. Click the device you'll be installing to (see [Dependencies: Hardware](#hardware) above for info).
1. Click **CHOOSE OS**
1. Click **Raspberry Pi OS (other)**
1. Click **Raspberry Pi OS Lite (32-bit)**
1. Click **CHOOSE STORAGE**
1. Click the target MicroSD card.
1. Click **NEXT**
1. Click **EDIT SETTINGS**

#### General Tab:

1. Check **Set hostname:** and enter `heads-tails`
1. Check **Set username and password**
1. **Username**: `heads-tails`
1. **Password**: `Heads I Win!`
1. Check **Configure wireless LAN**
1. **SSID**: Set to match your wifi network name
1. **Password**: Enter the password for your wifi network
1. **Wireless LAN country**: US (or wherever you happen to be)
1. Check **Set locale settings**
1. **Time zone**: Match to your timezone
1. **Keyboard layout**: us (or whatever keybaord layout you're using)

#### Services Tab:

1. Check **Enable SSH**
1. Check **Use password authentication** 
1. Click **SAVE**

#### Flash the MicroSD card:

1. Click **YES** to apply the OS customization settings. 
1. Click **YES** to erase existing data on the target MicroSD card.
1. Enter the admin password to flash the card
1. Wait for flashing and verification to complete

### Set up Raspberry Pi Zero W

#### Connect, Boot Up, Log In:

1. Insert freshly flashed MicroSD into the Raspberry Pi Zero W.
1. Connect a USB keyboard (wireless OK) to the USB A to micro USB adapter (provided with kit).
1. Connect the micro USB adapter to the Raspberry Pi
1. Connect the micro HDMI to HDMI adapter (provided with kit).
1. Connect to an HDMI display (monitor or projector, etc.) and pwoer on the display.
1. Connect 5V micro USB power adapter (provided in kit)
1. When prompted for `heads-tails login:` type `heads-tails` and press `enter/return` on your USB keyboard.
1. When prompted for `Password:` type `Heads I Win!` and presse `enter/return`. Note: You will NOT see the characters you type. This is normal for Linux.

#### Install Software

1. Run (type then press enter): `ping google.com -c 5` to check that you're connected to the internet. Refer to [Additional Configuration: Configure to connect to WiFi](./guides/replace raspberry pi/replacement_guide.md#wifi) if you're not connected to the internet.
1. Run `sudo apt-get update`
1. Run `sudo apt-get upgrade`
1. Run `sudo apt-get install python3 python3-pigpio pigpiod git`
1. Clone this repository: `git clone https://github.com/phillipdavidstearns/heads-tails-lite.git`
1. Change into the repository directory: `cd heads-tails-lite`
1. Copy systemd service files: `sudo cp services/heads-tails-lite.service /lib/systemd/system/`
1. Update changes to systemd: `sudo systemctl daemon-reload`
1. Start the installed services: `sudo systemctl start heads-tails-lite`
1. Enable installed services to start on boot: `sudo systemctl enable heads-tails-lite`
1. Check the status of installed services: `systemctl status heads-tails-lite pigpiod`

```
● heads-tails-lite.service - heads-tails-lite main python script
   Loaded: loaded (/lib/systemd/system/heads-tails-lite.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2020-08-29 02:30:11 BST; 8h ago
 Main PID: 5642 (python3)
    Tasks: 2 (limit: 4915)
   CGroup: /system.slice/heads-tails-lite.service
           └─5642 /usr/bin/python3 /home/heads-tails/heads-tails-lite/python/heads-tails-lite.py

● pigpiod.service
   Loaded: loaded (/lib/systemd/system/pigpiod.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2020-08-29 02:30:11 BST; 8h ago
 Main PID: 5641 (pigpiod)
    Tasks: 6 (limit: 4915)
   CGroup: /system.slice/pigpiod.service
           └─5641 /usr/bin/pigpiod -g
```

## Testing Hardware

To aid in debugging issues with the hardware, the `test.py` script sequenctially lights headlight driver boards as well as dims and brightens the headlights.

### Using `test.py` as user `heads-tails`

1. Run: `cd`
1. Stop `heads-tails-lite.service` by running: `sudo systemctl stop heads-tails-lite`
1. Run the script: `sudo python3 heads-tails-lite/src/test.py`
1. To stop, press `ctrl+c`.
1. Restart `heads-tails-lite.service`: `sudo systemctl start heads-tails-lite`
