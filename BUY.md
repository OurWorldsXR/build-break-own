# What to buy to run this yourself

Everything one student needs to build a Sovereign Weather Station and take it
home, plus the few things the person running the room needs. Prices were
checked on 18 November 2026 and will drift. Where a price could not be
checked, it says **est.**

The software only cares about three things: the sensor is a BME280, the screen
is an SSD1306, and both run on I2C at 3.3 V. Any vendor's breakout that meets
that works. The links below are the parts we have used, or a trusted seller of
the same part.

## One kit, one student

This is Kit A, the breadboard kit. It is the one to buy.

| # | Part | Per kit | Where | Price | Per kit |
|---|---|---|---|---|---|
| 1 | **PocketBeagle 2** | 1 | [Mouser 713-102110780](https://www.mouser.com/ProductDetail/BeagleBoard-by-Seeed-Studio/102110780), [Digi-Key 102110780](https://www.digikey.com/en/products/detail/beagleboard/102110780/25927193) | about $30 to $45 depending on distributor and day | **$40** |
| 2 | **microSD card, 32 GB, high endurance** | 1 | [SanDisk High Endurance 32 GB, SDSQQNR-032G-GN6IA](https://www.adorama.com/sandisk-high-endurance-uhs-i-u3-microsd-memory-card/p/idsdsqqnr032) | $22.99 single | **$23** |
| 3 | **BME280 sensor, 4 pin, I2C** | 1 | [ProtoSupplies BME280 module](https://protosupplies.com/product/bme280-i2c-pressure-humidity-temperature-sensor-module/) | $5.95 | **$6** |
| 4 | **SSD1306 OLED screen, 0.96 inch, 128 x 64, I2C, 4 pin** | 1 | [Hosyond 5 pack on Amazon](https://www.amazon.com/dp/B09C5K91H7) | $14.98 for 5 | **$3** |
| 5 | **Mini breadboard, 170 point, no rails** | 1 | ELEGOO 6 pack (Amazon), or [Pimoroni colourful mini breadboard](https://shop.pimoroni.com/products/colourful-mini-breadboard) | about $9 for 6 (est.) | **$1.50** |
| 6 | **Jumper wires** | 12 male-to-male, 4 male-to-female | [ELEGOO 120 piece kit on Amazon](https://www.amazon.com/dp/B01EV70C78): 40 M-M, 40 M-F, 40 F-F | $6.98 per kit of 120 | **$2.50** |
| 7 | **USB-C data cable** | 1 | any cable that says *data* or *sync*. USB-C to USB-C for newer laptops, USB-A to USB-C for older ones | $3 to $6 in multi-packs (est.) | **$5** |
| | | | | **Per kit, with the board** | **about $81** |
| | | | | **Per kit, if the board is donated** | **about $41** |

Notes that save a workshop:

- **The card is the biggest cost after the board.** Multi-packs usually cost
  less per card than the single price above. Get 32 GB, not 16: the image
  unpacks to about 10 GB and needs room to log. Cheap no-name cards are the
  most likely part to fail at the table.
- **The jumper kit is shared.** One 120 piece kit covers three Kit A stations
  (40 male-to-male at 12 each) with a few spares. Buy one kit per three
  stations, plus one extra kit for the room.
- **The cable must carry data.** A charge-only cable powers the board and the
  laptop never sees it, which looks exactly like a dead board. It is the most
  common failure in the room. Test every cable before the day.

## Optional, per kit

| Part | Where | Price | Why |
|---|---|---|---|
| **DS3231 real time clock** | [ProtoSupplies DS3231 with EEPROM](https://protosupplies.com/product/ds3231-rtc-with-eeprom-module/) | $3.95, coin cell fitted | Real timestamps. The board has no network and no clock battery, so without this the time drifts every time power is cut. Four more male-to-male jumpers. |
| **USB power bank** | any, 5 V USB output | $10 to $20 (est.) | Runs the station away from the laptop: on a windowsill, outside, overnight. One per table is enough at the workshop; students who keep their kit will want their own. |

**Read this before buying any other DS3231.** Most cheap DS3231 modules (the
ZS-042 layout) have a charging circuit built for a *rechargeable* LIR2032
cell, and ship with or get fitted with a non-rechargeable CR2032. Charging a
CR2032 can make it heat, leak or burst. The ProtoSupplies module above has the
charging resistor removed already. For any other ZS-042 module, either buy
[LIR2032 rechargeable cells](https://www.batteryjunction.com/products/powerizer-lir2032)
($2.85 each) or remove the resistor. [HARDWARE.md](sovereign-weather-station/HARDWARE.md)
has the details.

## Once per room

| Thing | How many | Price |
|---|---|---|
| A laptop with a USB port | one per student or per pair | already there, or borrowed. Mac, Windows 10 or later and Linux all have `ssh` built in |
| USB microSD card reader | one per person flashing cards | $10 to $15 (est.). Only needed if your computer has no card slot |
| Spare kits | 10 to 20% of the room, bagged and tested | as above |
| A bag of loose jumpers | about 40 | one more ELEGOO kit, $6.98 |
| Printed [worksheet](worksheet.html) | one per student | printing |

Flash and boot every card once before the day.
[FLASHING.md](sovereign-weather-station/FLASHING.md) and the
[bench test](sovereign-weather-station/BENCH-TEST.md) walk through it.

## Kit B: no breadboard

If breadboards cannot reach you in time, leave out line 5 and use four
male-to-female jumpers (from the same ELEGOO kit) instead of twelve
male-to-male. The sensor and screen take turns on the same four wires.
Everything else is the same. It saves about $1.50 a kit and costs the moment
where both parts run together, so buy Kit A when you can.

## Buying in the UK

| Part | Where | Price |
|---|---|---|
| PocketBeagle 2 | [Farnell](https://uk.farnell.com/beagleboard/102110780/pocketbeagle-2/dp/4628782), [Digi-Key UK, 100003007](https://www.digikey.co.uk/en/products/detail/beagleboard/100003007/28118583) | £23 to £38 ex VAT, depending on part and listing |
| BME280 | [Adafruit 2652 at The Pi Hut](https://thepihut.com/products/adafruit-bme280-i2c-or-spi-temperature-humidity-pressure-sensor) | £13.40. Costs more, and is always the real part |
| Jumpers | [ELEGOO UK store, 120 piece kit](https://uk.elegoo.com/products/elegoo-multicolored-dupont-wire-kit) | |

Screens, breadboards, cards and cables: any UK seller of the same parts.

## Which board

Buy BeagleBoard part **102110780** from a US distributor, or **100003007**
from Farnell/element14 or Digi-Key UK. Both are the PocketBeagle 2. Every
board sold now is Rev A1 with the quad-core AM6254, though some listings still
name the older dual-core AM6232. **The station image runs on both revisions**
without changes. Avoid marketplace sellers far above list price.

## Do not buy

- **A BMP280 sold as a BME280.** Same package, same pins, no humidity sensor
  inside. Cheap multi-packs on marketplaces are the usual source. The station
  still runs on one, but the humidity reading, the part students breathe on,
  shows `--`. `sws-check` question 3 tells you which you have. On ProtoSupplies
  modules, the second line of the chip marking starts with **U** for a BME280
  and **K** for a BMP280.
- **A 0x3D screen.** A few SSD1306 modules ship at address 0x3D. The software
  looks at 0x3C. The ones above are 0x3C.
- **The original PocketBeagle** (2017, no "2"). Different chip, different
  image. It will not boot this card.
- **Push buttons and a soldering iron.** They were in our first order. The
  station does not use a button yet, and nothing in the build needs solder.

## Where these numbers came from

Checked 18 November 2026: Mouser (713-102110780, in stock), Digi-Key UK
(100003007, £38.13 ex VAT), Farnell UK (102110780, £23.21 ex VAT), Adorama
(SanDisk SDSQQNR-032G-GN6IA, $22.99), ProtoSupplies (BME280 $5.95, DS3231
$3.95), Amazon via SpecPicks (Hosyond 5 pack $14.98, ELEGOO 120 piece kit
$6.98), The Pi Hut (Adafruit 2652, £13.40), Battery Junction (LIR2032, $2.85).
The breadboard, cable and power bank lines are estimates.
