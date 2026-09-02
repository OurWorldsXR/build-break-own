# Sovereign Weather Station

A weather station on a PocketBeagle 2 with no way to send your data anywhere.
It reads the air. It writes to a card in your hand. It shows you six numbers.
You decide what leaves.

Built for Build It, Break It, Own It. OurWorlds, AISES 2026.

## Build it yourself

1. Flash the official PocketBeagle 2 Debian image with the
   [BeagleBoard Imaging Utility](https://www.beagleboard.org/bb-imager).
   Use its **Edit** button to set your username and password before writing.
2. Card in, USB-C to your laptop, wait about 30 seconds.
3. `ssh <you>@192.168.7.2`  (or `192.168.6.2` on a Mac)
4. Copy this repo to the board, then:
   ```
   sudo ./setup.sh
   sudo reboot
   ```
5. `sws-check`

Every change `setup.sh` makes is listed in [CHANGES.md](CHANGES.md). Read the
diff. That is the point.

## Wiring

| Board pin | Goes to | Carries |
|---|---|---|
| P1_14 | 3V3 on both modules | 3.3 volt power. never 5 |
| P1_15 | GND on both modules | ground |
| P1_26 | SDA on both modules | data |
| P1_28 | SCL on both modules | clock |

Check these against the PocketBeagle 2 P1 diagram before you wire anything.
They are inherited from the original PocketBeagle. Nobody has confirmed them on
PB2 hardware yet.

Sensor answers at `0x76` (sometimes `0x77`). Screen answers at `0x3C`.

## sws-check

Four questions, answered in plain language:

1. which I2C buses exist  (there is no `i2c-1` on this board)
2. what is answering on them
3. is the sensor a real BME280 (`0x60`) or a BMP280 in disguise (`0x58`)
4. can this station reach the internet  (no. and it shows you why)

## Tested, and not tested

```
python3 test/test_station.py
```

Runs the drivers against a simulated I2C bus: compensation maths, framebuffer
bounds, the font, the hourly flush, and whether the totals survive a restart.
21 checks, no hardware needed. It found a real bug the first time it ran: the pressure compensation was wrong
by a factor that would have logged nonsense for six months without crashing
anything. That is why it is here.

What it does not prove: that the pin numbers are right, or that the I2C bus
number is right. Hardware validation is underway. Expect the pinout and the bus
number to be corrected here once a board has confirmed them.

## Building the card image

There is no `.img` in this repo, on purpose. The build script is the artifact;
the image is what the script produces on your machine.

1. Flash the official PocketBeagle 2 Debian image from
   [beagleboard.org/distros](https://www.beagleboard.org/distros) using the
   [BeagleBoard Imaging Utility](https://www.beagleboard.org/bb-imager).
   Use its **Edit** button to set the username and password first.
2. Boot, connect over USB-C, `ssh <you>@192.168.7.2` (`192.168.6.2` on a Mac).
3. Copy this directory to the board and run `sudo ./setup.sh`, then reboot.
4. `sws-check`. Record what it prints; that output settles the bus number, the
   addresses and the chip ID in one go.
5. Once it is right, shut down cleanly and `dd` the card back to an `.img` on
   your laptop. That is the file you flash eleven more times.
6. `sws-firstboot` regenerates SSH host keys and machine-id on each clone, so
   twelve cards are not twelve identical machines.
