# Facilitator run sheet

For whoever is standing in the room. Assumes the [bench test](BENCH-TEST.md)
passed and every board has [booted once](FLASHING.md).

## The week before

- [ ] All 15 boards booted once with sensor and screen; screen came up on each
- [ ] 20 cards flashed and numbered; 15 in boards, 5 in a labeled bag
- [ ] Every kit bagged: board, card, USB-C cable, BME280, OLED, breadboard, 8+ jumpers, printed WIRING.md
- [ ] 3 spare kits bagged the same way
- [ ] A bag of 40 loose jumpers
- [ ] 2 USB power banks, charged
- [ ] Printed worksheets, one per team plus spares
- [ ] Your own laptop with `ssh` working and this repo cloned, offline copy
- [ ] Confirmed with AISES whether students bring laptops. If not, you need one laptop per team or the desktop configuration

## Room setup, 30 minutes before

- [ ] One kit per table, unopened
- [ ] Your demo station wired and running so students can see the target
- [ ] Wiring card visible at every table
- [ ] Power banks at the front for stations that finish early and want to run untethered

## The session, 20 minutes of building

**Minute 0.** Hold up the board. "Everything you are about to build, you will
also take apart on paper."

**Minutes 1 to 8, wire it.** Teams follow the wiring card. Facilitators walk
the room and check only two things at each table before the USB goes in: 3V3
is on VCC, GND is on GND. Say it out loud at each table. Then let them plug in.

**Minutes 8 to 12, watch it boot.** Screen comes up in about 40 seconds. A team
whose screen stays dark: unplug, recheck SDA and SCL, replug. Do not debug
past two attempts; swap the kit for a spare and move on. Debugging is not the
lesson.

**Minutes 12 to 20, talk to it.** Teams with laptops:

```
ssh student@192.168.7.2       # or .6.2 on a Mac. password: buildit
sws-check
sws-live
```

Have them breathe on the sensor during `sws-live`. Then `sws-check` question 4
is the pivot to the worksheet: no wifi, no bluetooth, no cellular. The only
way the number gets off this board is a person reading it.

Teams without laptops: the screen is enough. Three pages, five seconds each.

## The rest of the session

The worksheet. Seven layers, two questions each: who controls this, and where
do they answer to. Students trace the board they just used.

Points to put on the table when they get stuck:

- **Application.** The code is in `/opt/sws/station`. They can `cat` it. Who wrote it? Who can change it?
- **Userland.** Debian. Thousands of people, no company. Where is Debian based?
- **Kernel.** Linux. Look at `uname -a`. TI publishes the board support. Who is TI?
- **Bootloader.** U-Boot, open source. Look in `/boot/firmware`. Where is that code from?
- **Boot firmware.** The AM62's security core runs closed TI firmware first. Nobody outside TI can read it. This is the first wall.
- **Fabrication.** TI fabs in Texas, Japan and elsewhere. Which fab made this chip? Nobody in the room can find out.
- **Chip design.** ARM Cortex-A53 cores, licensed from ARM (UK, owned by SoftBank, Japan). TI's own design around them. Two countries before you reach silicon.

The board design itself is published: https://openbeagle.org/pocketbeagle/pocketbeagle-2.
A student can open the schematic and find pin P1.26. That is the point of
using this board. Most hardware stops them at the userland layer.

## Common failures, in order of likelihood

1. Charge-only USB-C cable. Board powers up, laptop never sees it. Swap cable.
2. SDA and SCL swapped. Screen dark, `sws-check` finds nothing. Swap the two wires.
3. Jumper not seated in the breadboard. Wiggle test.
4. Card not seated. Board LEDs never blink.
5. Laptop firewall or VPN blocking the USB network. Turn the VPN off.
6. BMP280 in a BME280's clothing. Works, no humidity. `sws-check` says so. Move on.

## After

- [ ] Every kit repacked as a kit, card left in the board
- [ ] Note which kits are known good and which were swapped out
- [ ] Kits go to the named recipient school or chapter, with a printed copy of README.md, WIRING.md and this file
- [ ] Attendance and completion count for the November 15 report
