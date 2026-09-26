# Sovereign Weather Station

A weather station on a PocketBeagle 2 with no way to send your data anywhere.
It reads the air. It writes to a card in your hand. It shows you six numbers.
You decide what leaves.

Built for Build It, Break It, Own It. OurWorlds, AISES 2026.

| Read this | When |
|---|---|
| [HARDWARE.md](HARDWARE.md) | ordering parts, or checking what a kit should contain |
| [FIRST-BUILD.md](FIRST-BUILD.md) | never wired a board before. start here, with the parts in front of you |
| [WIRING.md](WIRING.md) | at the table. print one per team |
| [BENCH-TEST.md](BENCH-TEST.md) | first time with a board in hand. do this before anything else |
| [FLASHING.md](FLASHING.md) | writing the image to twenty cards |
| [FACILITATOR.md](FACILITATOR.md) | running the room |
| [CHANGES.md](CHANGES.md) | exactly what this image adds to BeagleBoard's |

## Flash it

The card image is built by GitHub Actions from the official PocketBeagle 2
Debian image and this directory, and attached to each `station-v*` release:
https://github.com/OurWorldsXR/build-break-own/releases

1. Download `sovereign-weather-station-pocketbeagle2.img.xz` and check it
   against the `.sha256sum` next to it.
2. Write it with the [BeagleBoard Imaging Utility](https://www.beagleboard.org/bb-imager)
   or `xzcat ....img.xz | sudo dd of=/dev/sdX bs=4M status=progress`.
3. Card in, USB-C to your laptop, wait about 30 seconds.
4. `ssh student@192.168.7.2`  (or `192.168.6.2` on a Mac). Password `buildit`.
   Change it: `passwd`. The login is set on first boot from
   `sysconf.txt` on the card, so you can edit it there before booting too.
5. `sws-check`, then `sws-live` to watch the numbers move.

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

Confirmed against the PocketBeagle 2 expansion header table (P1.14 VDD_3V3,
P1.15 GND, P1.26 I2C2_SDA, P1.28 I2C2_SCL) and the board's device tree, which
enables `main_i2c2` on those pins at 400 kHz and gives it alias `i2c2`. So on
the official image the header bus is `/dev/i2c-2`. The code does not assume
that: it finds the bus through sysfs and falls back to looking.

`/dev/i2c-0` is the board's own bus (EEPROM at 0x50, ADC at 0x20). Leave it
alone. There is no `/dev/i2c-1`.

Sensor answers at `0x76` (sometimes `0x77`; both are handled). Screen answers
at `0x3C`. A DS3231 clock, if fitted, at `0x68`; `sws-rtc` binds it at boot
and sets the system time from it.

## sws-check

Five questions, answered in plain language:

1. which I2C buses exist  (there is no `i2c-1` on this board)
2. what is answering on the header bus
3. is the sensor a real BME280 (`0x60`) or a BMP280 in disguise (`0x58`)
4. what time does the board think it is, and how does it know
5. can this station reach the internet  (no. and it shows you why)

## Tested, and not tested

```
python3 test/test_station.py
```

Runs the drivers against a simulated I2C bus: compensation maths, framebuffer
bounds, the font, the hourly flush, and whether the totals survive a restart.
30 checks, no hardware needed. It found a real bug the first time it ran: the pressure compensation was wrong
by a factor that would have logged nonsense for six months without crashing
anything. That is why it is here.

What it does not prove: that a real BME280 and SSD1306 behave like the fake
ones. The pin numbers and bus come from BeagleBoard's own documentation and
device tree, not from a board on a bench. Rehearsal on real hardware is the
last step and is still owed.

## Building the card image

There is no `.img` in this repo, on purpose. The build script is the artifact;
the image is what the script produces. `build-image.sh` does it without a
board: it downloads the official image, checks its hash, mounts it, runs
`setup.sh` inside it through an arm64 chroot (qemu-user-static), writes the
first-boot login into `sysconf.txt`, and compresses the result. The GitHub
Actions workflow in `.github/workflows/build-image.yml` runs exactly that
script; push a `station-v*` tag and the image lands on the release page.

```
sudo ./build-image.sh            # needs xz, losetup, sfdisk, qemu-user-static
```

Or on a board, by hand:

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
