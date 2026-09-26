#!/usr/bin/env python3
"""Draws every picture in images/ and the print sheets in images/print/.
Run it after any change; never hand-edit the SVGs.

    python3 tools/draw-diagrams.py            # SVGs
    python3 tools/draw-diagrams.py --print    # also the A4 PDF (needs playwright + chromium)

Everything is drawn in millimetres at one scale (SCALE px per mm), so the
board, breadboard and modules keep their real relative sizes in every
picture. Real dimensions used:
  PocketBeagle 2           56 x 35 mm, headers 2 x 18 at 2.54 mm pitch
  half size breadboard     83 x 55 mm, 30 columns, 2.54 mm pitch
  BME280 breakout (4 pin)  11.5 x 15 mm
  0.96" SSD1306 module     27 x 27 mm, glass 24 x 13 mm
  DS3231 ZS-042 module     38 x 22 mm

Facts the drawings rest on (sources in HARDWARE.md and WIRING.md):
  header side of the PocketBeagle 2 = the side with the microSD slot and dog logo.
  Sockets up, USB-C to the right: P1 is the bottom strip, P2 the top.
  Pins 1/2 at the USB-C end, 35/36 at the far end. On P1 odd pins are the outer row.
  P1.14 VDD_3V3, P1.15 GND, P1.26 I2C2_SDA, P1.28 I2C2_SCL.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "images")
PRINT = os.path.join(OUT, "print")
os.makedirs(OUT, exist_ok=True); os.makedirs(PRINT, exist_ok=True)

SCALE = 6.4                      # px per mm, the common scale
PAGE_W, PAGE_H = 1400, 990       # A4 landscape proportions
RED, BLK, BLU, YEL = "#d62828", "#1c1c1c", "#1d6fd8", "#f2b705"
INK, MUTE, PAPER = "#1a1a1a", "#666666", "#ffffff"
BOARD, BOARD_EDGE, SOCKET, SOCKET_EDGE = "#26393a", "#0f1b1b", "#070b0b", "#5a6c6c"
BB, BB_EDGE, HOLE = "#f5f1e3", "#c5bda3", "#3b3b3b"
PCB_PURPLE, PCB_BLUE, PCB_NAVY = "#5b3f9e", "#1e4d8c", "#1d2340"
FONT = 'font-family="Inter, Helvetica, Arial, sans-serif"'
PITCH = 2.54
NAMES = {14: "VDD_3V3", 15: "GND", 26: "I2C2_SDA", 28: "I2C2_SCL"}
HOT = {14: RED, 15: BLK, 26: BLU, 28: YEL}
LABEL = {RED: "3.3 V", BLK: "ground", BLU: "SDA (data)", YEL: "SCL (clock)"}


def mm(v): return v * SCALE


class Page:
    def __init__(self, title, subtitle="", w=PAGE_W, h=PAGE_H):
        self.w, self.h = w, h
        self.o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>',
                  f'<rect width="{w}" height="{h}" fill="{PAPER}"/>']
        self.text(40, 52, title, 26, INK, weight=700)
        if subtitle:
            self.text(40, 80, subtitle, 15, MUTE)

    def add(self, s): self.o.append(s)

    def text(self, x, y, s, size=13, fill=INK, anchor="start", weight=400, extra=""):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>')

    def callout(self, x, y, n, color="#1d6fd8"):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{color}" stroke="#fff" stroke-width="2.5"/>')
        self.text(x, y + 5.5, str(n), 15, "#fff", "middle", 700)

    def wire(self, pts, color, width=5):
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        self.add(f'<path d="{d}" stroke="#fff" stroke-width="{width+4}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>')
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        for x, y in (pts[0], pts[-1]):
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{width+1.5}" fill="{color}" stroke="#fff" stroke-width="2"/>')

    def legend(self, x, y, colors=(RED, BLK, BLU, YEL)):
        self.add(f'<rect x="{x-12}" y="{y-24}" width="170" height="{len(colors)*26+14}" rx="8" fill="#f4f4f4"/>')
        for i, c in enumerate(colors):
            yy = y + i * 26
            self.add(f'<rect x="{x}" y="{yy-9}" width="34" height="9" rx="4.5" fill="{c}"/>')
            self.text(x + 44, yy, LABEL[c], 13)

    def save(self, name):
        self.add("</svg>")
        with open(os.path.join(OUT, name), "w") as f:
            f.write("\n".join(self.o))
        print("wrote", name)


# ---------------------------------------------------------------- components
class PB2:
    """PocketBeagle 2, header side up.
    usb_left=False: USB-C on the right, P1 is the bottom strip (BeagleBoard's own view).
    usb_left=True:  board turned 180 degrees, P1 is the top strip, pin 1 at the left."""
    W, H = 56, 35

    def __init__(self, p, x, y, usb_left=False, hot=None, numbers=True, scale=None):
        self.p, self.x, self.y, self.usb_left = p, x, y, usb_left
        self.hot = hot or {}
        self.numbers = numbers
        self.s = scale or SCALE
        self.pos = {}
        self.draw()

    def m(self, v): return v * self.s
    def pin_xy(self, pin): return self.pos[pin]

    def draw(self):
        p, x, y, m = self.p, self.x, self.y, self.m
        w, h = m(self.W), m(self.H)
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{m(6)}" fill="{BOARD}" stroke="{BOARD_EDGE}" stroke-width="2"/>')
        ux = x - m(1.2) if self.usb_left else x + w - m(1.6)
        p.add(f'<rect x="{ux}" y="{y+h/2-m(4.5)}" width="{m(2.8)}" height="{m(9)}" rx="{m(1.4)}" fill="#cfcfcf" stroke="#7a7a7a"/>')
        sdx = x + m(5) if self.usb_left else x + w - m(19)
        p.add(f'<rect x="{sdx}" y="{y+h/2-m(7.5)}" width="{m(14)}" height="{m(15)}" rx="{m(1)}" fill="#a9b6b6" stroke="#6d7a7a"/>')
        p.text(sdx + m(7), y + h / 2 + 4, "microSD", 10 * self.s / SCALE, "#1a2a2a", "middle")
        lx = x + w - m(20) if self.usb_left else x + m(20)
        p.text(lx, y + h / 2 + 4, "beagleboard.org", 10 * self.s / SCALE, "#b9c6c6", "middle", extra='font-style="italic"')
        col_x0 = (x + m(6.6)) if self.usb_left else (x + w - m(6.6))
        step = m(PITCH) * (1 if self.usb_left else -1)
        if self.usb_left:
            rows_P1 = (y + m(2.3), y + m(2.3 + PITCH)); rows_P2 = (y + h - m(2.3), y + h - m(2.3 + PITCH))
        else:
            rows_P1 = (y + h - m(2.3), y + h - m(2.3 + PITCH)); rows_P2 = (y + m(2.3), y + m(2.3 + PITCH))
        sq = m(1.9)
        for name, (outer, inner) in (("P1", rows_P1), ("P2", rows_P2)):
            for k in range(1, 19):
                cx = col_x0 + (k - 1) * step
                odd, even = 2 * k - 1, 2 * k
                for pin, yy in ((odd, outer), (even, inner)):
                    c = self.hot.get(pin) if name == "P1" else None
                    p.add(f'<rect x="{cx-sq/2}" y="{yy-sq/2}" width="{sq}" height="{sq}" rx="1.5" fill="{c or SOCKET}" stroke="{"#fff" if c else SOCKET_EDGE}" stroke-width="{1.8 if c else 0.8}"/>')
                    if name == "P1": self.pos[pin] = (cx, yy)
            p.text(col_x0 - step * 1.25, (outer + inner) / 2 + 4, name, 11 * self.s / SCALE, "#fff", "middle", 700)
            if self.numbers:
                above = outer < y + h / 2
                fs = 9 * self.s / SCALE
                for k, (a, b) in ((1, (1, 2)), (18, (35, 36))):
                    cx = col_x0 + (k - 1) * step
                    p.text(cx, (outer - 7) if above else (outer + 14), str(a), fs, "#e6e6e6", "middle")
                    p.text(cx, (inner + 14) if above else (inner - 7), str(b), fs, "#e6e6e6", "middle")


class Breadboard:
    """Half size breadboard, 30 columns, a rail pair on each long edge.
    Rows j..f above the groove, e..a below. The bottom rail pair is the one
    nearest the board, so that is where power goes in this build."""
    W, H = 83, 55

    def __init__(self, p, x, y):
        self.p, self.x, self.y = p, x, y
        self.draw()

    def col_x(self, c): return self.x + mm(4.6) + (c - 1) * mm(PITCH)
    # top pair (not used for power here, but real boards have it)
    def rail_top_plus(self): return self.y + mm(3.2)
    def rail_top_minus(self): return self.y + mm(3.2 + PITCH)
    # bottom pair: − nearer the rows, + on the outer edge
    def rail_minus(self): return self.y + mm(self.H) - mm(3.2 + PITCH)
    def rail_plus(self): return self.y + mm(self.H) - mm(3.2)
    def row_y(self, r):
        top, bot = "jihgf", "edcba"
        if r in top: return self.y + mm(9.8) + top.index(r) * mm(PITCH)
        return self.y + mm(9.8 + 5 * PITCH + 3.6) + bot.index(r) * mm(PITCH)

    def draw(self):
        p, x, y = self.p, self.x, self.y
        w, h = mm(self.W), mm(self.H)
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1.5)}" fill="{BB}" stroke="{BB_EDGE}" stroke-width="2"/>')
        d = mm(1.0)
        for rp, rm, sign_y in ((self.rail_top_plus(), self.rail_top_minus(), -1), (self.rail_plus(), self.rail_minus(), 1)):
            p.add(f'<line x1="{x+mm(3)}" y1="{rp-sign_y*mm(1.6)}" x2="{x+w-mm(3)}" y2="{rp-sign_y*mm(1.6)}" stroke="{RED}" stroke-width="2.5"/>')
            p.add(f'<line x1="{x+mm(3)}" y1="{rm+sign_y*mm(1.6)}" x2="{x+w-mm(3)}" y2="{rm+sign_y*mm(1.6)}" stroke="{BLU}" stroke-width="2.5"/>')
            p.text(x + mm(1.4), rp + 5, "+", 13, RED, weight=700); p.text(x + mm(1.4), rm + 5, "−", 13, BLU, weight=700)
            for c in range(1, 31):
                cx = self.col_x(c)
                for yy in (rp, rm):
                    p.add(f'<rect x="{cx-d/2}" y="{yy-d/2}" width="{d}" height="{d}" rx="1" fill="{HOLE}"/>')
        for c in range(1, 31):
            cx = self.col_x(c)
            for r in "jihgfedcba":
                yy = self.row_y(r)
                p.add(f'<rect x="{cx-d/2}" y="{yy-d/2}" width="{d}" height="{d}" rx="1" fill="{HOLE}"/>')
            if c == 1 or c % 5 == 0:
                p.text(cx, self.row_y("a") + mm(2.6), str(c), 8, MUTE, "middle")
                p.text(cx, self.row_y("j") - mm(1.4), str(c), 8, MUTE, "middle")
        for r in "jihgfedcba":
            p.text(x + mm(1.8), self.row_y(r) + 3, r, 8, MUTE)
        gy = (self.row_y("f") + self.row_y("e")) / 2
        p.add(f'<line x1="{x+mm(2)}" y1="{gy}" x2="{x+w-mm(2)}" y2="{gy}" stroke="#e0d9c4" stroke-width="{mm(1.4)}"/>')


def pins_down(p, x, y_edge, labels, pitch_px, tip_len, font=6.5):
    """Draw a row of header pins hanging off a module's bottom edge. Returns {label: tip xy}."""
    out = {}
    for i, l in enumerate(labels):
        px = x + (i - (len(labels) - 1) / 2) * pitch_px
        p.add(f'<line x1="{px}" y1="{y_edge}" x2="{px}" y2="{y_edge+tip_len}" stroke="#8d8d8d" stroke-width="2.6"/>')
        p.text(px, y_edge - mm(0.9), l, font, "#fff", "middle", 700)
        out[l] = (px, y_edge + tip_len)
    return out


def module_bme(p, x, y, tip=None):
    """HiLetgo style BME280, 4 pins on the bottom edge. x,y = top left of the PCB."""
    w, h = mm(11.5), mm(15)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1)}" fill="{PCB_PURPLE}" stroke="#2a1d4d"/>')
    p.add(f'<rect x="{x+w/2-mm(1.4)}" y="{y+mm(2.4)}" width="{mm(2.8)}" height="{mm(2.4)}" rx="1" fill="#c9c9d6" stroke="#8a8aa0"/>')
    p.add(f'<circle cx="{x+mm(2)}" cy="{y+mm(2)}" r="{mm(0.8)}" fill="none" stroke="#c9c9d6"/>')
    p.text(x + w / 2, y + mm(8.4), "BME280", 5.5, "#d9d2ee", "middle")
    return pins_down(p, x + w / 2, y + h, ["VIN", "GND", "SCL", "SDA"], mm(PITCH), tip if tip is not None else mm(3.5))


def module_oled(p, x, y, order=("GND", "VCC", "SCL", "SDA"), tip=None):
    """0.96 inch SSD1306 module, pins on the bottom edge (as it sits in the breadboard)."""
    w, h = mm(27), mm(27)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1.2)}" fill="{PCB_NAVY}" stroke="#0b0e1c"/>')
    p.add(f'<rect x="{x+mm(1.5)}" y="{y+mm(4)}" width="{mm(24)}" height="{mm(13)}" rx="1" fill="#05050a" stroke="#3a3a55"/>')
    p.text(x + w / 2, y + mm(11.6), "NOW  21.4 C", 8, "#8fd3ff", "middle", extra='font-family="monospace"')
    for cx_ in (x + mm(2), x + w - mm(2)):
        for cy_ in (y + mm(2), y + h - mm(2)):
            p.add(f'<circle cx="{cx_}" cy="{cy_}" r="{mm(0.8)}" fill="none" stroke="#9aa3c8"/>')
    return pins_down(p, x + w / 2, y + h, list(order), mm(PITCH), tip if tip is not None else mm(3.5))


def module_rtc(p, x, y, optional=True, tip=None):
    """ZS-042 DS3231 module, 6 pins on the bottom long edge."""
    w, h = mm(38), mm(22)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1)}" fill="{PCB_BLUE}" stroke="#0e2a50" stroke-dasharray="{"6 4" if optional else "none"}"/>')
    p.add(f'<circle cx="{x+w-mm(11)}" cy="{y+h/2-mm(1.2)}" r="{mm(9.5)}" fill="#dcdcdc" stroke="#8c8c8c" stroke-width="1.5"/>')
    p.text(x + w - mm(11), y + h / 2 + 1, "coin cell", 7, "#555", "middle")
    p.add(f'<rect x="{x+mm(3)}" y="{y+mm(4)}" width="{mm(8)}" height="{mm(5)}" rx="1" fill="#111" stroke="#444"/>')
    p.text(x + mm(7), y + mm(7.3), "DS3231", 5.5, "#ddd", "middle")
    out = {}
    labs = ["32K", "SQW", "SCL", "SDA", "VCC", "GND"]
    for i, l in enumerate(labs):
        px = x + mm(4.5) + i * mm(PITCH)
        t = tip if tip is not None else mm(3.5)
        p.add(f'<line x1="{px}" y1="{y+h}" x2="{px}" y2="{y+h+t}" stroke="#8d8d8d" stroke-width="2.6"/>')
        p.text(px, y + h - mm(0.9), l, 5.5, "#fff", "middle", 700)
        out[l] = (px, y + h + t)
    return out


def jumper(p, x, y, color, length_mm=40):
    L = mm(length_mm)
    p.add(f'<rect x="{x}" y="{y-3.5}" width="{mm(2.2)}" height="7" rx="1.5" fill="#222"/>')
    p.add(f'<rect x="{x+L-mm(2.2)}" y="{y-3.5}" width="{mm(2.2)}" height="7" rx="1.5" fill="#222"/>')
    p.add(f'<line x1="{x+mm(2.2)}" y1="{y}" x2="{x+L-mm(2.2)}" y2="{y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
    p.add(f'<line x1="{x-6}" y1="{y}" x2="{x}" y2="{y}" stroke="#aaa" stroke-width="1.5"/>')
    p.add(f'<line x1="{x+L}" y1="{y}" x2="{x+L+6}" y2="{y}" stroke="#aaa" stroke-width="1.5"/>')


def cable(p, x, y):
    p.add(f'<rect x="{x}" y="{y-mm(1.4)}" width="{mm(6)}" height="{mm(2.8)}" rx="{mm(1.2)}" fill="#cfcfcf" stroke="#7a7a7a"/>')
    p.add(f'<path d="M {x+mm(6)} {y} C {x+mm(20)} {y-mm(12)} {x+mm(30)} {y+mm(12)} {x+mm(44)} {y}" stroke="#2b2b2b" stroke-width="5" fill="none"/>')
    p.add(f'<rect x="{x+mm(44)}" y="{y-mm(1.4)}" width="{mm(6)}" height="{mm(2.8)}" rx="{mm(1.2)}" fill="#cfcfcf" stroke="#7a7a7a"/>')


def sdcard(p, x, y):
    w, h = mm(11), mm(15)
    p.add(f'<path d="M {x} {y+mm(2)} L {x+mm(2)} {y} L {x+w} {y} L {x+w} {y+h} L {x} {y+h} Z" fill="#232323" stroke="#555"/>')
    p.text(x + w / 2, y + h / 2 + 3, "32 GB", 7, "#eee", "middle")


# ------------------------------------------------------------------- pages
def page_kit():
    p = Page("What is in the bag", "Tip everything out and match each thing to a picture. Everything here is drawn at the same scale as every later picture.", h=1080)
    # row 1: board, breadboard, cable, card
    PB2(p, 60, 120)
    p.callout(60 - 26, 126, 1)
    p.text(60, 120 + mm(35) + 30, "PocketBeagle 2", 17, INK, weight=700)
    p.text(60, 120 + mm(35) + 52, "The computer. Two black strips of sockets (P1, P2) along the", 13, MUTE)
    p.text(60, 120 + mm(35) + 70, "long edges, tiny numbers at the strip ends. Hold it by the edges.", 13, MUTE)
    p.text(60, 120 + mm(35) + 88, "The side with the microSD slot and the dog logo is the side you use.", 13, MUTE)
    Breadboard(p, 520, 120)
    p.callout(520 - 26, 126, 2)
    p.text(520, 120 + mm(55) + 30, "Breadboard, half size", 17, INK, weight=700)
    p.text(520, 120 + mm(55) + 52, "A slab of holes. Red and blue lines mark the power rails on each long edge.", 13, MUTE)
    p.text(520, 120 + mm(55) + 70, "A mini board (17 columns, one rail pair) works too.", 13, MUTE)
    cx0 = 1110
    p.add(f'<rect x="{cx0}" y="{140-mm(1.4)}" width="{mm(6)}" height="{mm(2.8)}" rx="{mm(1.2)}" fill="#cfcfcf" stroke="#7a7a7a"/>')
    p.add(f'<path d="M {cx0+mm(6)} 140 C {cx0+mm(14)} {140-mm(10)} {cx0+mm(20)} {140+mm(10)} {cx0+mm(30)} 140" stroke="#2b2b2b" stroke-width="5" fill="none"/>')
    p.add(f'<rect x="{cx0+mm(30)}" y="{140-mm(1.4)}" width="{mm(6)}" height="{mm(2.8)}" rx="{mm(1.2)}" fill="#cfcfcf" stroke="#7a7a7a"/>')
    p.callout(cx0 - 26, 140, 3)
    p.text(cx0, 190, "USB-C cable", 17, INK, weight=700)
    p.text(cx0, 212, "Must be a data cable. A charge-only", 13, MUTE); p.text(cx0, 230, "cable looks identical and is the most", 13, MUTE); p.text(cx0, 248, "common reason nothing works.", 13, MUTE)
    sdcard(p, cx0, 300)
    p.callout(cx0 - 26, 310, 4)
    p.text(cx0 + mm(11) + 14, 316, "microSD card", 17, INK, weight=700)
    p.text(cx0 + mm(11) + 14, 338, "8 GB or more. Holds the", 13, MUTE); p.text(cx0 + mm(11) + 14, 356, "whole operating system.", 13, MUTE)
    # row 2: modules and jumpers
    y0 = 600
    module_bme(p, 70, y0)
    p.callout(70 - 26, y0 + 6, 5)
    p.text(40, y0 + mm(15) + 50, "BME280 sensor", 17, INK, weight=700)
    p.text(40, y0 + mm(15) + 72, "Fingernail sized, purple or blue, four pins", 13, MUTE)
    p.text(40, y0 + mm(15) + 90, "(a few have six): VIN or VCC, GND, SCL, SDA", 13, MUTE)
    p.text(40, y0 + mm(15) + 108, "in tiny letters. The small metal can is the", 13, MUTE)
    p.text(40, y0 + mm(15) + 126, "sensor itself. If the pins are loose in the", 13, MUTE)
    p.text(40, y0 + mm(15) + 144, "bag instead of soldered on, stop: that is", 13, MUTE)
    p.text(40, y0 + mm(15) + 162, "a different job.", 13, MUTE)
    module_oled(p, 340, y0)
    p.callout(340 - 26, y0 + 6, 6)
    p.text(340, y0 + mm(27) + 50, "OLED screen (SSD1306, 0.96 inch)", 17, INK, weight=700)
    p.text(340, y0 + mm(27) + 72, "A square board with a dark glass window and four pins on", 13, MUTE)
    p.text(340, y0 + mm(27) + 90, "one edge: VCC, GND, SCL, SDA. The order of VCC and GND", 13, MUTE)
    p.text(340, y0 + mm(27) + 108, "differs between makers. Read yours now and write it down.", 13, INK, weight=700)
    p.text(340, y0 + mm(27) + 126, "Getting those two backwards is the one mistake in this", 13, MUTE)
    p.text(340, y0 + mm(27) + 144, "guide that kills a part instantly.", 13, MUTE)
    module_rtc(p, 760, y0 + 20)
    p.callout(760 - 26, y0 + 26, 7)
    p.text(760, y0 + mm(22) + 70, "DS3231 clock (optional)", 17, INK, weight=700)
    p.text(760, y0 + mm(22) + 92, "The one with the round coin cell holder. Six pins;", 13, MUTE)
    p.text(760, y0 + mm(22) + 110, "only SCL, SDA, VCC, GND are used. Leave it in the", 13, MUTE)
    p.text(760, y0 + mm(22) + 128, "bag on your first build. No battery until you have", 13, MUTE)
    p.text(760, y0 + mm(22) + 146, "read the battery note in HARDWARE.md.", 13, MUTE)
    jx = 1090
    p.callout(jx - 26, y0 + 6, 8)
    p.text(jx, y0 + 12, "Jumper wires", 17, INK, weight=700)
    p.text(jx, y0 + 34, "Male to male: a pin at both ends.", 13, MUTE)
    p.text(jx, y0 + 52, "12 needed, 16 with the clock.", 13, MUTE)
    for i, c in enumerate((RED, BLK, BLU, YEL)):
        jumper(p, jx, y0 + 80 + i * 26, c, 24)
        p.text(jx + mm(24) + 14, y0 + 85 + i * 26, LABEL[c], 13, INK)
    p.text(jx, y0 + 200, "Any four colours work if you use", 13, MUTE)
    p.text(jx, y0 + 218, "them the same way throughout.", 13, MUTE)
    p.text(40, 1080 - 30, "Not in the bag and not needed: a monitor, keyboard or power supply for the board. Your laptop is all three, through the USB-C cable.", 13, INK)
    p.save("kit.svg")


def page_mat():
    p = Page("Lay it out like this before you start", "This is the arrangement every later picture uses. You sit at the bottom edge. Cable and card stay where they are until Parts 3 and 4.", h=1080)
    mx, my, mw, mh = 60, 105, 1280, 950
    p.add(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="10" fill="#fcfcfc" stroke="#c4c4c4" stroke-dasharray="10 7" stroke-width="2"/>')
    p.text(mx + mw - 14, my + mh - 12, "your table, seen from above", 12, MUTE, "end")

    def zone(x, y, w, h, n, title):
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#eef3fa" stroke="#9db4d3" stroke-width="1.5"/>')
        p.callout(x + 24, y + 24, n)
        p.text(x + 48, y + 30, title, 15, INK, weight=700)

    z1h = 280
    zone(mx + 15, my + 15, 430, z1h, 1, "Modules, pins toward you")
    module_bme(p, mx + 60, my + 80); p.text(mx + 60 + mm(5.75), my + 80 + mm(15) + 40, "sensor", 12, MUTE, "middle")
    module_oled(p, mx + 200, my + 62); p.text(mx + 200 + mm(13.5), my + 62 + mm(27) + 40, "screen", 12, MUTE, "middle")
    p.text(mx + 35, my + z1h - 34, "Screen pin order, left to right:  ____  ____  ____  ____", 13, INK)
    p.text(mx + 35, my + z1h - 12, "Clock stays in the bag today.", 12, MUTE)
    zone(mx + 460, my + 15, 500, z1h, 2, "Jumpers in four rows, by colour")
    for i, (c, n) in enumerate([(RED, "4 red"), (BLK, "4 black"), (BLU, "3 blue"), (YEL, "3 yellow")]):
        for k in range(3):
            jumper(p, mx + 500 + k * 130, my + 90 + i * 40, c, 17)
        p.text(mx + 900, my + 95 + i * 40, n, 13, INK)
    p.text(mx + 480, my + z1h - 12, "Count them now. Hunting for a missing wire at step 3 costs ten minutes of doubt.", 12, MUTE)
    zone(mx + 975, my + 15, 290, z1h, 3, "Not yet")
    sdcard(p, mx + 1010, my + 70); p.text(mx + 1010 + mm(11) + 14, my + 96, "card: Part 3", 13, INK)
    cable(p, mx + 1000, my + 210); p.text(mx + 1000, my + 246, "cable: Part 4, not before", 13, INK)
    p.text(mx + 1000, my + z1h - 12, "Laptop closed, to one side.", 12, MUTE)
    z4y = my + 15 + z1h + 12; z4h = 372
    zone(mx + 15, z4y, 1250, z4h, 4, "Breadboard, the long way across")
    Breadboard(p, mx + 330, z4y + 12)
    p.text(mx + 35, z4y + 70, "Modules go along the top edge.", 13, INK)
    p.text(mx + 35, z4y + 90, "Power uses the rail pair along", 13, INK)
    p.text(mx + 35, z4y + 110, "the bottom edge, nearest the", 13, INK)
    p.text(mx + 35, z4y + 130, "board. If your board has one", 13, INK)
    p.text(mx + 35, z4y + 150, "rail pair only, turn it so that", 13, INK)
    p.text(mx + 35, z4y + 170, "pair is at the bottom.", 13, INK)
    p.text(mx + 900, z4y + 70, "Rows j to f (top half) hold the", 13, MUTE)
    p.text(mx + 900, z4y + 90, "modules and the two shared", 13, MUTE)
    p.text(mx + 900, z4y + 110, "columns. Rows e to a are", 13, MUTE)
    p.text(mx + 900, z4y + 130, "unused; wires fly over them.", 13, MUTE)
    z5y = z4y + z4h + 12; z5h = my + mh - 15 - z5y
    zone(mx + 15, z5y, 1250, z5h, 5, "PocketBeagle 2, sockets up, USB-C port to the LEFT")
    PB2(p, mx + 420, z5y + 12 + 6, usb_left=True)
    p.text(mx + 900, z5y + 60, "Turned so P1 is the strip nearest the", 13, INK)
    p.text(mx + 900, z5y + 80, "breadboard. Pin 1 is then at the left end", 13, INK)
    p.text(mx + 900, z5y + 100, "of P1, by the USB-C port.", 13, INK)
    p.text(mx + 900, z5y + 124, "Find the tiny printed 1 and 2 there", 13, INK, weight=700)
    p.text(mx + 900, z5y + 144, "before going on.", 13, INK, weight=700)
    p.text(mx + 900, z5y + 174, "Every wire that leaves P1 goes straight", 13, MUTE)
    p.text(mx + 900, z5y + 194, "up into the breadboard.", 13, MUTE)
    p.save("layout-mat.svg")


def page_board_pins():
    p = Page("Where the four pins are", "Board held with the sockets facing you and the USB-C port on the right, as BeagleBoard photographs it. On your table it is turned round; the numbers are the same.", h=880)
    b = PB2(p, 100, 120, usb_left=False, hot=HOT, scale=SCALE * 2.1)
    x1, y1 = b.pin_xy(1)
    p.add(f'<circle cx="{x1}" cy="{y1}" r="19" fill="none" stroke="{RED}" stroke-width="3"/>')
    p.text(x1 + 10, y1 + 64, "P1.1 is 5 V. Nothing ever goes in here.", 14, RED, "end", 700)
    zx, zy, zp = 100, 700, 42
    p.text(zx, zy - 26, "P1 close up. Column 1 is at the USB-C end. Outer row = odd pins, inner row = even pins.", 15, INK, weight=700)
    p.add(f'<rect x="{zx-16}" y="{zy-12}" width="{18*zp+32}" height="104" rx="10" fill="{BOARD}"/>')
    for k in range(1, 19):
        x = zx + (18 - k) * zp + zp / 2
        for pin, y in ((2 * k, zy + 18), (2 * k - 1, zy + 62)):
            c = HOT.get(pin)
            p.add(f'<rect x="{x-16}" y="{y-16}" width="32" height="32" rx="4" fill="{c or SOCKET}" stroke="{"#fff" if c else SOCKET_EDGE}" stroke-width="{2 if c else 1}"/>')
            p.text(x, y + 5, str(pin), 13, ("#fff" if c != YEL else INK) if c else "#9fb0b0", "middle", 700 if c else 400)
        p.text(x, zy + 110, str(k), 10, MUTE, "middle")
    p.text(zx - 18, zy + 110, "column", 10, MUTE, "end")
    p.text(zx + 18 * zp + 26, zy + 23, "inner row", 11, MUTE); p.text(zx + 18 * zp + 26, zy + 67, "outer row", 11, MUTE)
    p.text(zx + 18 * zp + 26, zy + 110, "USB-C end", 11, MUTE)
    lx = 940
    p.text(lx, 150, "The four we use", 17, INK, weight=700)
    for i, (pin, what, where) in enumerate(((14, "3.3 V out", "column 7, inner row"), (15, "ground", "column 8, outer row"), (26, "SDA, data", "column 13, inner row"), (28, "SCL, clock", "column 14, inner row"))):
        y = 192 + i * 64
        p.add(f'<rect x="{lx}" y="{y-20}" width="30" height="30" rx="4" fill="{HOT[pin]}"/>')
        p.text(lx + 15, y + 1, str(pin), 13, "#fff" if HOT[pin] != YEL else INK, "middle", 700)
        p.text(lx + 44, y - 4, f"P1.{pin}  {NAMES[pin]}", 15, INK, weight=700)
        p.text(lx + 44, y + 16, f"{what}. {where}, from the USB-C end.", 13, MUTE)
    p.text(lx, 480, "Trust the numbers printed on the board over", 13, INK, weight=700)
    p.text(lx, 498, "this picture. Find the printed 1 and 2 at the", 13, INK, weight=700)
    p.text(lx, 516, "USB-C end of P1 and the 35 and 36 at the far", 13, MUTE)
    p.text(lx, 534, "end. If they are there, the columns are right.", 13, MUTE)
    p.save("board-pins.svg")


def page_wiring():
    p = Page("The four wires, as a schematic", "The same four wires for every module: power, ground, data, clock. This is the whole circuit.")
    b = PB2(p, 60, 130, usb_left=False, hot=HOT, scale=SCALE * 1.5)
    bw = 56 * SCALE * 1.5
    rx = {RED: 60 + bw + 90, BLK: 60 + bw + 130, BLU: 60 + bw + 170, YEL: 60 + bw + 210}
    top, bot = 130, 940
    for c, x in rx.items():
        p.add(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="{c}" stroke-width="6" stroke-linecap="round"/>')
        p.text(x, top - 12, LABEL[c].split(" ")[0], 12, c, "middle", 700)
    drops = {14: 40, 15: 70, 26: 100, 28: 130}
    for pin, c in HOT.items():
        x, y = b.pin_xy(pin)
        p.wire([(x, y), (x, y + drops[pin]), (rx[c], y + drops[pin])], c, 5)
    for pin, dy in ((14, -13), (15, -13), (26, -13), (28, -27)):
        x, y = b.pin_xy(pin)
        p.text(x, y + dy, f"P1.{pin}", 10, "#fff", "middle", 700)
    p.text((rx[RED] + rx[YEL]) / 2, bot + 24, "breadboard: two rails and two shared columns", 12, MUTE, "middle")

    def block(x, y, title, sub, pins, addr, optional=False):
        w, h = 470, 60 + 26 * len(pins) + 34
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{"#fbfbfb" if optional else "#f2f6ff"}" stroke="{"#9a9a9a" if optional else "#3b4a6b"}" stroke-width="2" stroke-dasharray="{"8 5" if optional else "none"}"/>')
        p.text(x + 18, y + 28, title, 17, INK, weight=700)
        p.text(x + 18, y + 48, sub, 12, MUTE)
        for i, (lab, c) in enumerate(pins):
            yy = y + 74 + i * 26
            p.add(f'<rect x="{x+10}" y="{yy-8}" width="16" height="16" rx="3" fill="{c or "#fff"}" stroke="{INK if c else "#aaa"}"/>')
            p.text(x + 36, yy + 5, lab, 13, INK if c else "#999")
            if c: p.wire([(rx[c], yy), (x + 10, yy)], c, 5)
        p.text(x + 18, y + h - 14, addr, 12, MUTE)
        return h
    x = rx[YEL] + 60; y = 130
    y += block(x, y, "BME280 sensor", "temperature, pressure, humidity. 3.3 V logic",
               [("VIN / VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU), ("CSB, SDO: leave open (6-pin boards only)", None)],
               "answers at 0x76 or 0x77. chip ID 0x60 = BME280, 0x58 = BMP280") + 18
    y += block(x, y, "SSD1306 OLED, 128 x 64", "read the silkscreen: VCC and GND order varies by vendor",
               [("VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU)], "answers at 0x3C") + 18
    block(x, y, "DS3231 real time clock  (optional)", "keeps time on a coin cell when the board is off",
          [("VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU), ("32K, SQW: leave open", None)],
          "answers at 0x68. 0x57 is the EEPROM on the same module", optional=True)
    p.save("wiring.svg")


STEP_TITLES = {1: "Step 1 of 4: seat the modules", 2: "Step 2 of 4: power to each module", 3: "Step 3 of 4: the two shared columns", 4: "Step 4 of 4: four wires from the board"}
STEP_SUBS = {1: "Push each module into the top half so every pin has its own column. The module body sits over the rails. USB cable still in the bag.",
             2: "Red from each VCC or VIN column to the bottom + rail, black from each GND column to the bottom − rail. Read the module's letters before each wire.",
             3: "Column 8 collects every SDA (blue). Column 10 collects every SCL (yellow). Nothing plugs into 8 or 10 directly; they are meeting points.",
             4: "Red P1.14 to the + rail, black P1.15 to the − rail, blue P1.26 to column 8, yellow P1.28 to column 10. Then check every wire out loud."}


SENSOR_C, OLED_C, RTC_C = 2, 12, 21      # first pin column of each module
SDA_C, SCL_C = 8, 10                      # the two shared columns


def page_step(step):
    p = Page(STEP_TITLES[step], STEP_SUBS[step])
    bb = Breadboard(p, 330, 250)
    cx = bb.col_x
    rp, rm = bb.rail_plus(), bb.rail_minus()
    yj = bb.row_y("j")
    tip = mm(3.5)
    module_bme(p, cx(SENSOR_C) + mm(PITCH) * 1.5 - mm(11.5) / 2, yj - tip - mm(15))
    module_oled(p, cx(OLED_C) + mm(PITCH) * 1.5 - mm(27) / 2, yj - tip - mm(27))
    module_rtc(p, cx(RTC_C) - mm(4.5), yj - tip - mm(22))
    p.text(cx(SENSOR_C + 1.5), yj - tip - mm(15) - 10, "sensor", 12, INK, "middle", 700)
    p.text(cx(OLED_C + 1.5), yj - tip - mm(27) - 10, "screen: use YOUR pin order", 12, INK, "middle", 700)
    p.text(cx(RTC_C) - mm(4.5) + mm(19), yj - tip - mm(22) - 10, "clock (optional, later)", 12, MUTE, "middle", 700)
    if step >= 3:
        for c, col in ((SDA_C, BLU), (SCL_C, YEL)):
            p.add(f'<rect x="{cx(c)-mm(1.4)}" y="{yj-mm(1.4)}" width="{mm(2.8)}" height="{bb.row_y("f")-yj+mm(2.8)}" rx="3" fill="{col}" opacity="0.16"/>')
            p.text(cx(c), (bb.row_y("f") + bb.row_y("e")) / 2 + 4, str(c), 11, col, "middle", 700)
    plan = ((SENSOR_C, ["+", "-", "SCL", "SDA"]), (OLED_C, ["-", "+", "SCL", "SDA"]), (RTC_C, [None, None, "SCL", "SDA", "+", "-"]))
    off = mm(PITCH) / 2   # flying wires run between columns so they never look plugged in
    if step >= 2:
        for c0, order in plan:
            for i, t in enumerate(order):
                col = c0 + i
                if t == "+":
                    x = cx(col); p.wire([(x, bb.row_y("h")), (x + off, bb.row_y("h") + 10), (x + off, rp - 10), (x, rp)], RED)
                elif t == "-":
                    x = cx(col); p.wire([(x, bb.row_y("i")), (x + off, bb.row_y("i") + 10), (x + off, rm - 10), (x, rm)], BLK)
    if step >= 3:
        for c0, order in plan:
            for i, t in enumerate(order):
                col = c0 + i
                if t == "SCL": p.wire([(cx(col), bb.row_y("g")), (cx(col), bb.row_y("g") + 7), (cx(SCL_C), bb.row_y("g") + 7), (cx(SCL_C), bb.row_y("g"))], YEL)
                elif t == "SDA": p.wire([(cx(col), bb.row_y("f")), (cx(col), bb.row_y("f") + 7), (cx(SDA_C), bb.row_y("f") + 7), (cx(SDA_C), bb.row_y("f"))], BLU)
    yb = 250 + mm(55) + 60
    board = PB2(p, 330 + (mm(83) - mm(56)) / 2, yb, usb_left=True, hot=HOT if step == 4 else None)
    if step == 4:
        for pin, c, col in ((14, RED, 29), (15, BLK, 28)):
            x, y = board.pin_xy(pin); ry = rp if pin == 14 else rm
            drop = yb - 30 - (0 if pin == 14 else 14)
            p.wire([(x, y), (x, drop), (cx(col) + off, drop), (cx(col) + off, ry + 8), (cx(col), ry)], c)
        for pin, c, col in ((26, BLU, SDA_C), (28, YEL, SCL_C)):
            x, y = board.pin_xy(pin)
            drop = yb - 62 if pin == 26 else yb - 46
            tx = cx(col) - off if pin == 26 else cx(col) + off
            # ends in the TOP half of the shared column (row h), same net as the module wires
            p.wire([(x, y), (x, drop), (tx, drop), (tx, bb.row_y("h") + 6), (cx(col), bb.row_y("h"))], c)
        for pin, dx in ((14, 0), (15, 0), (26, -22), (28, 22)):
            x, y = board.pin_xy(pin)
            p.text(x + dx, y + 30, f"P1.{pin}", 10, "#fff", "middle", 700)
        p.text(40, PAGE_H - 30, "Say it out loud: red leaves 14 and arrives at +. Black leaves 15 and arrives at −. Blue leaves 26 and arrives at column 8. Yellow leaves 28 and arrives at column 10.", 13, INK)
    if step == 1:
        c = 16
        p.add(f'<rect x="{cx(c)-mm(1.4)}" y="{bb.row_y("e")-mm(1.4)}" width="{mm(2.8)}" height="{bb.row_y("a")-bb.row_y("e")+mm(2.8)}" rx="3" fill="none" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="5 3"/>')
        p.add(f'<rect x="{cx(c)+16}" y="{bb.row_y("d")-14}" width="330" height="62" rx="6" fill="#fff" stroke="#2a9d8f"/>')
        p.text(cx(c) + 24, bb.row_y("d") + 4, "One column of five holes is one wire inside the board.", 11, "#2a9d8f")
        p.text(cx(c) + 24, bb.row_y("c") + 4, "Each rail (+ or −) is one wire from end to end.", 11, "#2a9d8f")
        p.text(cx(c) + 24, bb.row_y("b") + 4, "The groove keeps the top half apart from the bottom.", 11, "#2a9d8f")
        p.text(40, PAGE_H - 30, "Press each module in firmly and evenly; it takes more force than you expect. Pins in row j, one pin per column. The bodies hang over the top edge and cover the top rails, which is why power uses the bottom rails.", 13, INK)
    if step == 2:
        p.text(40, PAGE_H - 30, "Power uses the bottom rail pair, the one nearest the board. The wire leaves the module's column at row h or i and runs down past the groove to the rail. It only connects at its two ends.", 13, INK)
    if step == 3:
        p.text(40, PAGE_H - 30, "Two blue wires end in column 8 and nowhere else. Two yellow wires end in column 10. A blue wire never touches a yellow column. Both columns sit between the sensor and the screen.", 13, INK)
    p.legend(1200, 150)
    p.text(1200 - 12, 290, "board turned so P1 faces the", 11, MUTE); p.text(1200 - 12, 306, "breadboard: USB-C on the left,", 11, MUTE); p.text(1200 - 12, 322, "pin 1 at the left end of P1.", 11, MUTE)
    p.text(1200 - 12, 350, "the rails: follow the printed red", 11, MUTE); p.text(1200 - 12, 366, "and blue lines on your own board;", 11, MUTE); p.text(1200 - 12, 382, "which one is outer varies.", 11, MUTE)
    p.save(f"bench-step{step}.svg")
    if step == 4:
        with open(os.path.join(OUT, "bench-step4.svg")) as f: data = f.read()
        with open(os.path.join(OUT, "bench-layout.svg"), "w") as f: f.write(data)
        print("wrote bench-layout.svg")


def print_pdf():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed; skipping the PDF"); return
    pages = ["kit", "layout-mat", "board-pins", "bench-step1", "bench-step2", "bench-step3", "bench-step4", "wiring"]
    html = ["<html><head><meta charset='utf-8'><style>@page{size:A4 landscape;margin:8mm} html,body{margin:0;padding:0} .pg{width:281mm;height:194mm;display:flex;align-items:center;justify-content:center;overflow:hidden} .pg+.pg{page-break-before:always} img{max-width:281mm;max-height:194mm;width:auto;height:auto}</style></head><body>"]
    for n in pages:
        html.append(f"<div class='pg'><img src='../{n}.svg'></div>")
    html.append("</body></html>")
    idx = os.path.join(PRINT, "sheets.html")
    with open(idx, "w") as f: f.write("".join(html))
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None)
        pg = b.new_page()
        pg.goto("file://" + idx)
        pg.pdf(path=os.path.join(PRINT, "FIRST-BUILD-sheets.pdf"), format="A4", landscape=True, print_background=True,
               margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"})
        b.close()
    os.remove(idx)
    print("wrote print/FIRST-BUILD-sheets.pdf")


if __name__ == "__main__":
    page_kit(); page_mat(); page_board_pins(); page_wiring()
    for i in (1, 2, 3, 4): page_step(i)
    if "--print" in sys.argv: print_pdf()
