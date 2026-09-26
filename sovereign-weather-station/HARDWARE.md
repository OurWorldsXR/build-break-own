# Hardware

What one station is, what was ordered on each side of the Atlantic, and what
to check on each part before you trust it. The software only cares that the
sensor is a BME280, the screen is an SSD1306 and the optional clock is a
DS3231, all on I2C at 3.3 V. Any vendor's breakout works.

## The board

**PocketBeagle 2, revision A1, TI AM6254.** Quad Cortex-A53 at 1.4 GHz, 512 MB
DDR4, microSD, USB-C. BeagleBoard.org part number 102110780.

| Where | Part number | Note |
|---|---|---|
| Farnell / element14 (UK) | BeagleBoard 100003007 | "PocketBeagle 2 Board, ARM Cortex-A53/M4F". This is the A1 / AM6254 board |
| Digi-Key, Mouser (US) | search "PocketBeagle 2" | every unit sold since the first run is A1 / AM6254 |
| TI.com | BEAGL-POCKETBEAGLE-2 | same board |

Revision A0 with the dual core AM6232 is out of production. If you have one,
it works the same: same headers, same pinout, same device tree
(`k3-am62-pocketbeagle2`), same Debian image. **One image serves both the UK
and the US kits.** There is nothing to build twice.

## The modules

### BME280: temperature, pressure, humidity

I2C breakout, 3.3 V. Two common shapes:

- **4 pin** (VIN, GND, SCL, SDA). The HiLetgo "BME280 3.3V" in the US order is this one. Address 0x76.
- **6 pin** (VCC, GND, SCL, SDA, CSB, SDO). Leave CSB and SDO unconnected for I2C at 0x76. Tie SDO to 3V3 and it moves to 0x77. The software handles both.

**The BMP280 problem.** A BMP280 is the same chip package on the same breakout
with no humidity sensor inside, and vendors ship them under BME280 listings.
The chip ID tells the truth: `sudo i2cget -y 2 0x76 0xD0` gives `0x60` for a
BME280 and `0x58` for a BMP280. `sws-check` does this for you. A BMP280 still
runs the station; humidity shows as `--`.

### SSD1306: 0.96 inch OLED, 128 x 64, I2C

Four pins. **The order of VCC and GND on the header varies by vendor**, and
both orders exist on boards that look identical. Read the silkscreen on each
one before wiring; do not copy the neighbor's board. Address 0x3C (a few are
0x3D; the software only looks at 0x3C, so if a screen stays dark and
`i2cdetect` shows `3d`, it is a 0x3D unit and needs the solder jumper on its
back moved, or swap it out).

The Hosyond 0.96" in the US order is this part. Runs on 3.3 V.

### DS3231: real time clock (optional, US kits)

The hiBCTR module in the US order is the common "ZS-042" layout: a DS3231 and
an AT24C32 EEPROM on one board with a coin cell holder. Six pins on one edge:
32K, SQW, SCL, SDA, VCC, GND. Only SCL, SDA, VCC, GND are used. Addresses:
0x68 (clock) and 0x57 (the EEPROM, which we ignore).

**Battery warning, read this.** The ZS-042 has a trickle charging circuit
meant for a rechargeable LIR2032. The order includes **CR2032** cells, which
are not rechargeable. Charging a CR2032 makes it heat, leak or burst. Before
fitting a CR2032, disable the charger: remove the 200 ohm resistor next to the diode
(marked `R5` on most of these boards) or cut the trace to it. With that resistor gone the
module draws only microamps from the cell and keeps time for years. If you
are not comfortable removing a surface mount resistor, buy LIR2032 cells
instead and leave the module as is.

Why it is worth fitting: the board has no network, so it has no other way to
know the time. Without a DS3231, `fake-hwclock` restores the time from the
last shutdown and every power cut puts the clock behind by the length of the
outage. With it, timestamps in `/data/readings.csv` are real.

### Breadboard and jumpers: the part that defines the kit

The US order has ELEGOO 170 point mini breadboards (17 columns, no power
rails) and Dupont jumper packs. With a breadboard the station runs sensor
and screen together: that is **Kit A**. Without one, four male-to-female
jumpers run one module at a time straight from the board: **Kit B**. The
UK bench is Kit B until a breadboard arrives. FIRST-BUILD.md has both.

Kit A wants 12 male-to-male jumpers per station (16 with the clock). Kit B
wants 4 male-to-female. Jumpers are the part that goes missing; bring 40
spares loose, of both kinds.

### Cable

USB-C **data** cable. A charge only cable powers the board and the laptop
never sees it, which looks exactly like a dead board. This is the single most
common failure at a table.

### Card

8 GB or more. The order has 32 GB SanDisk High Endurance, which is a good
choice for a logger that writes hourly for months.

## What was ordered

### UK

Farnell order, August 2026: **2 x 100003007** PocketBeagle 2 (A1, AM6254).
Accessories for the UK bench (sensor, screen, breadboard, cable, card) come
from the same list as the US kit; any of the parts above work.

### US

Amazon.com, shipping to OurWorlds, San Diego, September 2026:

| Item | Listings | Per station |
|---|---|---|
| HiLetgo BME280 3.3 V sensor | 4 | 1 |
| SanDisk 32 GB High Endurance microSD | 3 | 1, plus spares |
| Hosyond 0.96" SSD1306 OLED, I2C (5 pack) | 3 (15 screens) | 1 |
| hiBCTR DS3231 RTC with AT24C32 (10 pack) | 2 (20 clocks) | 1, optional |
| ELEGOO mini breadboard (6 pack) | 4 (24 boards) | 1 |
| ELEGOO Dupont jumper wire, 120 pcs | 2 | 8 to 12 |
| Smays USB-C cable (10 pack) | 1 (10 cables) | 1 |
| GENSROCK power bank (2 pack) | 1 | shared |
| 16 mm momentary push buttons, 24 pcs | 1 | future use, see below |
| CR2032 batteries (10 pack) | 2 (20 cells) | 1 per RTC. see the battery warning |
| 22 AWG 4 conductor wire, 50 ft | 1 | for permanent builds after the workshop |
| 60 W soldering iron kit | 1 | for the R5 removal and permanent builds |

**Counts to confirm against the order page** before assuming 15 stations are
covered: the BME280 and microSD lines may be single units, not packs. If they
are, you have 4 sensors and 3 cards. Ten USB-C cables against 15 boards is
also short. Boards for the US side: no BeagleBoard order was found in the
inbox that was searched; check sal@ourworlds.io, Catherine's orders, and the
BeagleBoard donation route.

### The push buttons

Not wired yet. The plan is one button per station between a GPIO pin and
ground, so a student can step through the screen pages by hand instead of
waiting for the five second rotation. Candidate pin: P2.02 (GPIO0_45), a
plain GPIO with no other role on the header. The software change is small and
lands once a board has confirmed the pin. Until then the screen rotates on
its own and the buttons stay in the bag.

## Voltage, once more

Everything on the P1 and P2 headers is 3.3 V. Power every module from P1.14
(VDD_3V3). P1.01 is 5 V in and will kill a 3.3 V sensor.

## Where the kits go afterwards

Every kit is donated at the close of the session to an Oregon tribal school
or AISES student chapter. Pack the kits so they leave as kits: board, card,
cable, sensor, screen, clock, breadboard, jumpers, a printed WIRING.md.
