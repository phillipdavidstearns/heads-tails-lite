# Heads Tails Lite

A piece by Madeline Hollander

## Codebase

Python code to run lighting control on a Raspberry Pi:

* Main script: `heads-tails-lite.py`
* GPIO helper script: `IO.py`
* File loading script: `fileHandlers.py`
* Test routine: `test.py`

## Dependencies

### Hardware

* Raspberry Pi (tested on Raspberry Pi 3 B+, 4 B, Zero W)

### Software

* python3 (should come pre-installed on Raspberry Pi): `sudo apt-get install python3.7`
* [pigpio python](http://abyz.me.uk/rpi/pigpio/python.html): `sudo apt-get install python3-pigpio pigpiod`
* RPi.GPIO (should come pre-installed on Raspberry Pi): `sudo apt-get install python3-rpi.gpio`

## Installation

1. Create a user `heads-tails`: `sudo useradd -m -G wheel heads-tails`
1. Switch to user `heads-tails`: `su heads-tails`
1. Change to the home directory for `heads-tails`: `cd ~`
1. Clone this repository: `git clone https://github.com/phillipdavidstearns/heads-tails-lite.git`
1. Change into the repository directory: `cd heads-tails-lite`
1. Copy systemd service files: `sudo cp -R services/* /lib/systemd/system/`
1. Update changes to systemd: `sudo systemctl daemon-reload`
1. Start the installed services: `sudo systemctl start heads-tails-lite pigpiod`
1. Enable installed services to start on boot: `sudo systemctl enable heads-tails-lite pigpiod`
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

1. `cd ~`
1. Stop `heads-tails-lite.service`: `sudo systemctl stop heads-tails-lite`
1. Run the script: `sudo python3 heads-tails-lite/python/test.py`
1. To stop, press `ctrl+c`.
1. Restart `heads-tails-lite.service`: `sudo systemctl start heads-tails-lite`
