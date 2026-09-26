# What this image adds to BeagleBoard's

Base: official BeagleBoard.org PocketBeagle 2 Debian image from
https://www.beagleboard.org/distros . Nothing in the base is removed or patched.

## Packages installed
| Package | Why |
|---|---|
| `python3-smbus2` | talking to the I2C bus |
| `i2c-tools` | `i2cdetect`, `i2cget`: the commands the workshop uses |
| `fake-hwclock` | saves the time at shutdown. see "the clock problem" below |

## Files added
| Path | What |
|---|---|
| `/opt/sws/station/bme280.py` | sensor driver, datasheet compensation written out |
| `/opt/sws/station/ssd1306.py` | screen driver, 5x7 font, no image library |
| `/opt/sws/station/station.py` | the logger. reads every 5 min, writes hourly |
| `/opt/sws/bin/sws-check` | the verification tool students run |
| `/opt/sws/bin/sws-live` | prints a reading every two seconds. for the table |
| `/opt/sws/BUILD.txt` | when it was built, from what, and the hash of every file above |
| `/opt/sws/bin/sws-firstboot` | makes each cloned card a distinct machine |
| `/etc/systemd/system/station.service` | starts the logger at boot |
| `/etc/systemd/system/sws-firstboot.service` | runs once, ever |
| `/data/` | the only directory that gets written to |

## Boot partition
`sysconf.txt`: `user_name=student`, `user_password=buildit`. The base image's
own first-boot service creates that login and then blanks the file. Change the
password at the workshop or edit the file before first boot.

## Services enabled
`station.service`, `sws-firstboot.service`, `fake-hwclock.service`

## Nothing else
No network configuration is added or changed. No wifi, no bluetooth, no
cellular hardware exists on this board. `sws-check` question 4 proves it.

## The clock problem
There is no network, so there is no NTP. There is no RTC backup battery, so the
clock does not survive a power cut. `fake-hwclock` stores the time at shutdown
and restores it at boot, which keeps timestamps in order but lets them drift.

For real timestamps, fit a **DS3231 RTC module** (about $4) on the same I2C bus
as the sensor. It keeps time for years on a coin cell. `setup.sh` detects one if
present and says so.

## Card wear
Readings are held in RAM and written once an hour: 12 writes a day instead of
288. A power cut costs at most one hour of data. `/data` is the only thing
written during normal operation.
