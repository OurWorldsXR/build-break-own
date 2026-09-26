# Wiring card

Print one per table. Four wires. Both modules share all four.

```
PocketBeagle 2, P1 header (the header on the USB-C side)

   P1.14  VDD_3V3  ──────┬──── VCC  (BME280)
                         └──── VCC  (OLED)

   P1.15  GND      ──────┬──── GND  (BME280)
                         └──── GND  (OLED)

   P1.26  SDA      ──────┬──── SDA  (BME280)
                         └──── SDA  (OLED)

   P1.28  SCL      ──────┬──── SCL  (BME280)
                         └──── SCL  (OLED)
```

Use the breadboard rails. One rail is 3.3 V, one is ground. SDA and SCL each
get a row. Then each module drops its four pins into the matching places.

## Before you plug in the USB cable

1. Count the pins twice. The numbers are printed on the board next to the header.
2. 3V3 goes to VCC. Ground goes to GND. Get these two wrong and the sensor dies.
3. SDA to SDA, SCL to SCL. Get these two swapped and nothing answers, but nothing breaks.
4. Nothing goes to P1.01. That pin is 5 V.

## What "working" looks like

Screen lights up within about 40 seconds of power and shows `NOW` with a
temperature. Every five seconds it changes page: `NOW`, `SINCE START`,
`MONTH CARD`.

## What the pins are

| Pin | Name on the board | Job |
|---|---|---|
| P1.14 | VDD_3V3 | 3.3 volt power out |
| P1.15 | GND | ground |
| P1.26 | I2C2_SDA | data, both directions |
| P1.28 | I2C2_SCL | clock, board sets the pace |

These are the pins of the AM62's `main_i2c2` controller. On the official Debian
image that controller is `/dev/i2c-2`. `/dev/i2c-0` is the board talking to
itself (its EEPROM and ADC). There is no `/dev/i2c-1`.

## Who answers on the bus

| Address | Device |
|---|---|
| `0x3C` | the screen |
| `0x76` or `0x77` | the sensor (depends on the breakout) |

Run `sws-check` to see them. Run `sudo i2cdetect -y -r 2` to see them the
long way.
