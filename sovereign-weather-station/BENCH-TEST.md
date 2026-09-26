# Bench test

Do this once, on one board, before flashing twenty cards. It takes about an
hour the first time. It splits into two halves so a failure points at the
wiring or at the software, not at both.

## Half one: the wiring, using BeagleBoard's own image

This half uses nothing from this repo. If it passes, the hardware is right.

1. **Wire one station** per [WIRING.md](WIRING.md). Nothing plugged in yet.

2. **Flash BeagleBoard's image.** Install the
   [BeagleBoard Imaging Utility](https://www.beagleboard.org/bb-imager).
   Board: PocketBeagle 2. Image: the newest "Debian ... IoT" entry. Press
   **Edit**, set a username and password, write the card.

3. **Boot.** Card in. USB-C to the laptop. Wait 30 to 40 seconds. The board's
   power LED comes on immediately; the user LEDs start blinking when Linux is up.

4. **Connect.**
   ```
   ssh <yourname>@192.168.6.2        # Mac
   ssh <yourname>@192.168.7.2        # Windows, Linux
   ```
   First time: answer `yes` to the host key question.

5. **Look at the buses.**
   ```
   ls /dev/i2c-*
   ```
   Expect `/dev/i2c-0  /dev/i2c-2  /dev/i2c-3`. No `i2c-1`. That is correct.

6. **Look at the header bus.**
   ```
   sudo i2cdetect -y -r 2
   ```
   In the grid, expect `3c` in row 30 and `76` (or `77`) in row 70. With a
   DS3231 fitted, also `57` in row 50 and `68` in row 60.

   | You see | It means |
   |---|---|
   | `3c` and `76`/`77` | wiring is right. go to half two |
   | only `3c` | sensor's four wires; check SDA/SCL on the sensor side |
   | only `76`/`77` | screen's four wires |
   | nothing | 3V3 or GND not reaching the breadboard rails, or SDA/SCL swapped at the board |
   | `command not found` | `sudo apt install i2c-tools`. needs internet: on a Mac, System Settings, General, Sharing, Internet Sharing, share to the BeagleBone interface. or skip to half two, which has the tool built in |

7. **Prove the sensor is a BME280 and not a BMP280.**
   ```
   sudo i2cget -y 2 0x76 0xD0      # use 0x77 if that is where it answered
   ```
   `0x60` is a BME280. `0x58` is a BMP280: it works, but with no humidity.
   The vendor sold you the wrong part; the software will say so on screen.

Half one passed. Write down which address the sensor answered at.

## Half two: the software, using our image

1. **Get the image.** From
   https://github.com/OurWorldsXR/build-break-own/releases, download
   `sovereign-weather-station-pocketbeagle2.img.xz` and its `.sha256sum`.

2. **Check it.**
   ```
   shasum -a 256 -c sovereign-weather-station-pocketbeagle2.img.xz.sha256sum   # Mac
   sha256sum -c sovereign-weather-station-pocketbeagle2.img.xz.sha256sum       # Linux
   ```
   Must say `OK`. If not, download again.

3. **Flash it** with the Imaging Utility ("Use custom" / choose file). No Edit
   step this time: the image sets the login itself.

4. **Boot and connect.** Same as before. Login `student`, password `buildit`.
   ```
   ssh student@192.168.6.2
   ```
   If ssh refuses because the host key changed (it will; it is a different
   image on the same address):
   ```
   ssh-keygen -R 192.168.6.2
   ```
   and try again.

5. **Run the check.**
   ```
   sws-check
   ```
   Five questions. Question 2 should list `0x3C` and the sensor address (and
   `0x68` if a clock is fitted). Question 3 should say "real BME280".
   Question 4 says where the time came from. Question 5 should say there is
   no radio on this board.

6. **Watch it work.**
   ```
   sws-live
   ```
   A reading every two seconds. Breathe on the sensor: humidity climbs, then
   falls back. Cup a hand over it: temperature climbs. `Ctrl-C` to stop.

7. **Look at the screen.** It should already be showing readings and changing
   page every five seconds. If the screen is blank but `sws-check` saw `0x3C`,
   restart the logger and read its log:
   ```
   sudo systemctl restart station
   journalctl -u station -n 30
   ```

8. **Check the logger is logging.** Wait five minutes, then:
   ```
   systemctl status station
   ls -la /data
   ```
   `station.service` is `active (running)`. `/data/readings.csv` appears after
   the first hourly flush, or immediately after a clean shutdown:
   ```
   sudo poweroff
   ```
   wait for the LEDs to stop, unplug, replug, ssh back in, `cat /data/readings.csv`.

9. **Check the board made itself unique.**
   ```
   hostname                  # sws-xxxxxx, six random characters
   cat /data/station-id
   ```
   Every card cloned from this image gets its own name on first boot.

10. **Change the password** if this board is leaving the room:
    ```
    passwd
    ```

Half two passed. Now flash the rest: [FLASHING.md](FLASHING.md).

## When something fails

| Symptom | First thing to try |
|---|---|
| `ssh: connect ... Connection refused` or timeout | wait another 30 s. then check the laptop sees a new network interface. try the other address. try a different USB-C cable (charge-only cables are the usual cause) |
| board never boots (no blinking LEDs) | card not fully seated, or the flash did not finish. reflash |
| `sws-check` finds no buses at all | not our image, or not a PocketBeagle 2 |
| `sws-check` question 2: nothing answered | wiring. go back to half one |
| `sws-check` says BMP280 | wrong part from the vendor. still runs, no humidity |
| screen shows garbage | loose SDA or SCL wire. reseat, `sudo systemctl restart station` |
| readings are absurd (pressure 0, temperature -40) | run `python3 /opt/sws/test/test_station.py` and open an issue with the output of `sws-live` |
| clock is 1970 or stale | expected on a board with no DS3231. fit one (see HARDWARE.md, battery note first), then `sudo systemctl restart sws-rtc` and set it once: `sudo date -u -s '2026-10-14 09:00:00' && sudo hwclock -w --utc` |

Open an issue at https://github.com/OurWorldsXR/build-break-own/issues with
the output of `sws-check` pasted in. That output is designed to be the bug report.
