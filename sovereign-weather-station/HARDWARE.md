# Hardware

What one station is, what the whole workshop needs, and what each part costs.
Prices are Digi-Key list as of August 2026. Any equivalent part works; the
software only cares that the sensor is a BME280 and the screen is an SSD1306
on I2C.

## One station

| Part | What to look for | Approx. |
|---|---|---|
| PocketBeagle 2 | BeagleBoard.org, TI AM6232, 512 MB. The only board this image boots on | $40 |
| microSD card | 8 GB or more. 32 GB is what we ordered. Class 10 or A1 | $9 |
| USB-C cable | Data cable, not charge-only. Powers the board and carries the network link to the laptop | $5 |
| BME280 breakout | Temperature, pressure, humidity. I2C, 3.3 V. Four pins minimum: VCC/VIN, GND, SCL, SDA. Reports chip ID `0x60`. A BMP280 looks identical and reports `0x58`; it has no humidity sensor and the software says so | $10 |
| SSD1306 OLED | 128 x 64, I2C, 0.96 inch, address `0x3C`. Four pins: VCC, GND, SCL, SDA | $4 |
| Breadboard and jumpers | Half size breadboard, male to male jumpers, at least 8 | $9 |
| A laptop | Anything with a USB port that can run `ssh`. The board appears as a network device at 192.168.7.2 (Windows, Linux) or 192.168.6.2 (Mac) | students' own |

Optional: DS3231 real time clock module, about $4, on the same four wires.
Without it the clock drifts between power cycles. `setup.sh` detects it.

## The whole workshop

Twelve teams of four, plus three spare stations. Ordered:

| Item | Qty |
|---|---|
| PocketBeagle 2 | 15 |
| USB-C cable | 15 |
| 32 GB microSD | 20 (five spares; cards fail and get lost) |
| BME280 | 15 |
| SSD1306 OLED | 15 |
| Breadboard and jumper set | 15 |
| Printed worksheets and facilitator packs | 1 per team + spares |
| USB power bank or 5 V supply | a few, for stations running untethered |

Bring extra jumpers. Jumpers are the part that goes missing.

## Voltage

Everything on the P1 header is 3.3 V. The BME280 and most OLED breakouts
tolerate 3.3 V only on their logic pins even when the breakout says 5 V on the
power pin. Power both from P1.14 (VDD_3V3). Never from P1.01 (VIN_5V).

## Where the kits go afterwards

Every kit is donated at the close of the session to an Oregon tribal school or
AISES student chapter. Pack the kits so they leave as kits: board, card, cable,
sensor, screen, breadboard, jumpers, a printed copy of WIRING.md.
