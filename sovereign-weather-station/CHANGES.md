# What this image adds to BeagleBoard's

## station-v2 (November 2026)

Everything we learned on the bench and at AISES. **If your card was flashed
with station-v1, reflash it with station-v2.** You do not need to understand
the list below for that to fix it.

| What was wrong in v1 | What v2 does |
|---|---|
| `sws-firstboot` failed on every boot (`tr \| head` under `pipefail`), so no board got its own name and every boot made new ssh keys: "host key changed" over and over | reads three random bytes with `od`, finishes, and never runs again |
| `sws-rtc` set the clock from `/dev/rtc0`, which is the board's own clock with no battery, so a fitted DS3231 put the time back to 1970 | finds the rtc that belongs to the chip at 0x68 (usually `/dev/rtc1`), waits for it to appear, reads that one, and links it as `/dev/rtc-ds3231` |
| `sws-check` question 4 called `/dev/rtc0` the DS3231 | looks for the DS3231 by its device, and says so when it is not there |
| the screen could show noise ("snow") at power up, or after a wire moved | the screen's whole memory is written before the display is turned on, and the screen is set up again every five minutes and whenever it stops answering |
| the logger exited when there was no sensor, so a Kit B screen wired on its own never lit | runs with sensor and screen, either one alone, and picks up a part that is wired in later without a reboot |
| no way to find a station's name or address without a laptop | for twenty seconds after boot, and whenever there is no sensor, the screen shows the station's name and both USB addresses |

The one thing software cannot fix: the 4-pin screen modules have no reset pin.
If the screen still shows noise, unplug the USB cable, count to ten, plug it
back in. A full power off is the only reset that screen has.

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
| `/opt/sws/test/test_station.py` | the unit tests. `python3 /opt/sws/test/test_station.py` runs them on the board |
| `/opt/sws/BUILD.txt` | when it was built, from what, and the hash of every file above |
| `/opt/sws/bin/sws-firstboot` | makes each cloned card a distinct machine |
| `/opt/sws/bin/sws-rtc` | binds a DS3231 at 0x68 if wired, sets the clock from it, links it as `/dev/rtc-ds3231` |
| `/etc/systemd/system/station.service` | starts the logger at boot |
| `/etc/systemd/system/sws-firstboot.service` | runs once, ever |
| `/etc/systemd/system/sws-rtc.service` | every boot, before the logger |
| `/data/` | the only directory that gets written to |

## Boot partition
`sysconf.txt`: `user_name=student`, `user_password=buildit`. The base image's
own first-boot service creates that login and then blanks the file. Change the
password at the workshop or edit the file before first boot.

## Services enabled
`station.service`, `sws-firstboot.service`, `sws-rtc.service`, `fake-hwclock.service`

## Nothing else
No network configuration is added or changed. No wifi, no bluetooth, no
cellular hardware exists on this board. `sws-check` question 4 proves it.

## The clock problem
There is no network, so there is no NTP. There is no RTC backup battery, so the
clock does not survive a power cut. `fake-hwclock` stores the time at shutdown
and restores it at boot, which keeps timestamps in order but lets them drift.

For real timestamps, fit a **DS3231 RTC module** (about $4) on the same I2C bus
as the sensor. It keeps time for years on a coin cell. `sws-rtc` finds it at
every boot and sets the system clock from it. Set the clock once after fitting:
`sudo date -u -s '<UTC time>' && sudo hwclock -f /dev/rtc-ds3231 -w --utc`.
Without `-f`, `hwclock` writes to the board's own clock, which forgets it.

## Card wear
Readings are held in RAM and written once an hour: 12 writes a day instead of
288. A power cut costs at most one hour of data. `/data` is the only thing
written during normal operation.
