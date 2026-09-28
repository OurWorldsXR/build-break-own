#!/usr/bin/env python3
"""Draws every picture in images/ and the print sheets in images/print/.
Run it after any change; never hand-edit the SVGs.

    python3 tools/draw-diagrams.py            # SVGs
    python3 tools/draw-diagrams.py --print    # also the A4 PDFs (needs playwright + chromium)

Two kits, decided by the supply chain rather than by design:

  Kit A, breadboard.   A 170 point mini breadboard (17 columns, no power
                       rails) joins the modules to the board. Sensor and
                       screen run together. This is the US order.
  Kit B, direct.       No breadboard. Four male-to-female jumpers from the
                       board's sockets straight to one module at a time.
                       Sensor first, screen second. This is the UK bench
                       until a breadboard arrives, and works anywhere.

Everything is drawn in millimetres at one scale (SCALE px per mm) so parts
keep their real relative sizes. Real dimensions used:
  PocketBeagle 2           56 x 35 mm, headers 2 x 18 at 2.54 mm pitch
  mini breadboard          45 x 35 mm, 17 columns x 10 rows, 2.54 mm pitch, no rails
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

SCALE = 6.8                      # px per mm, the common scale
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
    def __init__(self, title, subtitle="", w=PAGE_W, h=PAGE_H, tag=""):
        self.w, self.h = w, h
        self.o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>',
                  f'<rect width="{w}" height="{h}" fill="{PAPER}"/>']
        self.text(40, 52, title, 26, INK, weight=700)
        if subtitle:
            self.text(40, 80, subtitle, 15, MUTE)
        if tag:
            self.add(f'<rect x="{w-232}" y="26" width="192" height="34" rx="17" fill="{"#1d6fd8" if tag.startswith("Kit A") else "#7a4fb0"}"/>')
            self.text(w - 136, 49, tag, 14, "#fff", "middle", 700)

    def add(self, s): self.o.append(s)

    def text(self, x, y, s, size=13, fill=INK, anchor="start", weight=400, extra=""):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>')

    def lines(self, x, y, rows, size=13, fill=INK, lh=20, weight=400):
        for i, r in enumerate(rows):
            self.text(x, y + i * lh, r, size, fill, weight=weight)

    def callout(self, x, y, n, color="#1d6fd8"):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{color}" stroke="#fff" stroke-width="2.5"/>')
        self.text(x, y + 5.5, str(n), 15, "#fff", "middle", 700)

    def wire(self, pts, color, width=5, curve=False):
        if curve and len(pts) == 2:
            (x1, y1), (x2, y2) = pts
            d = f"M {x1:.1f} {y1:.1f} C {x1:.1f} {(y1+y2)/2:.1f} {x2:.1f} {(y1+y2)/2:.1f} {x2:.1f} {y2:.1f}"
        else:
            d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        self.add(f'<path d="{d}" stroke="#fff" stroke-width="{width+4}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>')
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        for x, y in (pts[0], pts[-1]):
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{width+1.5}" fill="{color}" stroke="#fff" stroke-width="2"/>')

    def arc(self, a, b, color, lift, width=5):
        """A jumper that arches over the board between two holes in the same row."""
        (x1, y1), (x2, y2) = a, b
        d = f"M {x1:.1f} {y1:.1f} C {x1:.1f} {y1-lift:.1f} {x2:.1f} {y2-lift:.1f} {x2:.1f} {y2:.1f}"
        self.add(f'<path d="{d}" stroke="#fff" stroke-width="{width+4}" fill="none" stroke-linecap="round" opacity="0.95"/>')
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round"/>')
        for x, y in (a, b):
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
        f = self.s / SCALE
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{m(6)}" fill="{BOARD}" stroke="{BOARD_EDGE}" stroke-width="2"/>')
        ux = x - m(1.2) if self.usb_left else x + w - m(1.6)
        p.add(f'<rect x="{ux}" y="{y+h/2-m(4.5)}" width="{m(2.8)}" height="{m(9)}" rx="{m(1.4)}" fill="#cfcfcf" stroke="#7a7a7a"/>')
        sdx = x + m(5) if self.usb_left else x + w - m(19)
        p.add(f'<rect x="{sdx}" y="{y+h/2-m(7.5)}" width="{m(14)}" height="{m(15)}" rx="{m(1)}" fill="#a9b6b6" stroke="#6d7a7a"/>')
        p.text(sdx + m(7), y + h / 2 + 4, "microSD", 10 * f, "#1a2a2a", "middle")
        lx = x + w - m(20) if self.usb_left else x + m(20)
        p.text(lx, y + h / 2 + 4, "beagleboard.org", 10 * f, "#b9c6c6", "middle", extra='font-style="italic"')
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
            p.text(col_x0 - step * 1.25, (outer + inner) / 2 + 4, name, 11 * f, "#fff", "middle", 700)
            if self.numbers:
                above = outer < y + h / 2
                fs = 9 * f
                for k, (a, b) in ((1, (1, 2)), (18, (35, 36))):
                    cx = col_x0 + (k - 1) * step
                    p.text(cx, (outer - 7) if above else (outer + 14), str(a), fs, "#e6e6e6", "middle")
                    p.text(cx, (inner + 14) if above else (inner - 7), str(b), fs, "#e6e6e6", "middle")


class MiniBreadboard:
    """170 point mini breadboard: 17 columns, rows j..f above the groove and
    e..a below, no power rails. 45 x 35 mm."""
    W, H = 45, 35
    COLS = 17

    def __init__(self, p, x, y):
        self.p, self.x, self.y = p, x, y
        self.draw()

    def col_x(self, c): return self.x + mm(2.2) + (c - 1) * mm(PITCH)
    def row_y(self, r):
        top, bot = "jihgf", "edcba"
        if r in top: return self.y + mm(3.4) + top.index(r) * mm(PITCH)
        return self.y + mm(3.4 + 5 * PITCH + 3.0) + bot.index(r) * mm(PITCH)

    def draw(self):
        p, x, y = self.p, self.x, self.y
        w, h = mm(self.W), mm(self.H)
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1)}" fill="{BB}" stroke="{BB_EDGE}" stroke-width="2"/>')
        d = mm(1.0)
        for c in range(1, self.COLS + 1):
            cx = self.col_x(c)
            for r in "jihgfedcba":
                yy = self.row_y(r)
                p.add(f'<rect x="{cx-d/2}" y="{yy-d/2}" width="{d}" height="{d}" rx="1" fill="{HOLE}"/>')
            p.text(cx, y + h + 14, str(c), 9, MUTE, "middle")
        for r in "jihgfedcba":
            p.text(x - 10, self.row_y(r) + 3, r, 9, MUTE, "end")
        gy = (self.row_y("f") + self.row_y("e")) / 2
        p.add(f'<line x1="{x+mm(1)}" y1="{gy}" x2="{x+w-mm(1)}" y2="{gy}" stroke="#e0d9c4" stroke-width="{mm(1.2)}"/>')


def pins_down(p, x, y_edge, labels, pitch_px, tip_len, font=7):
    out = {}
    for i, l in enumerate(labels):
        px = x + (i - (len(labels) - 1) / 2) * pitch_px
        p.add(f'<line x1="{px}" y1="{y_edge}" x2="{px}" y2="{y_edge+tip_len}" stroke="#8d8d8d" stroke-width="3"/>')
        p.text(px, y_edge - mm(0.8), l, font, "#fff", "middle", 700)
        out[l] = (px, y_edge + tip_len)
    return out


def module_bme(p, x, y, tip=None):
    w, h = mm(11.5), mm(15)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1)}" fill="{PCB_PURPLE}" stroke="#2a1d4d"/>')
    p.add(f'<rect x="{x+w/2-mm(1.4)}" y="{y+mm(2.4)}" width="{mm(2.8)}" height="{mm(2.4)}" rx="1" fill="#c9c9d6" stroke="#8a8aa0"/>')
    p.add(f'<circle cx="{x+mm(2)}" cy="{y+mm(2)}" r="{mm(0.8)}" fill="none" stroke="#c9c9d6"/>')
    p.text(x + w / 2, y + mm(8.6), "BME280", 6.5, "#d9d2ee", "middle")
    return pins_down(p, x + w / 2, y + h, ["VIN", "GND", "SCL", "SDA"], mm(PITCH), tip if tip is not None else mm(3.5))


def module_oled(p, x, y, order=("GND", "VCC", "SCL", "SDA"), tip=None):
    w, h = mm(27), mm(27)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1.2)}" fill="{PCB_NAVY}" stroke="#0b0e1c"/>')
    p.add(f'<rect x="{x+mm(1.5)}" y="{y+mm(4)}" width="{mm(24)}" height="{mm(13)}" rx="1" fill="#05050a" stroke="#3a3a55"/>')
    p.text(x + w / 2, y + mm(11.6), "NOW  21.4 C", 9, "#8fd3ff", "middle", extra='font-family="monospace"')
    for cx_ in (x + mm(2), x + w - mm(2)):
        for cy_ in (y + mm(2), y + h - mm(2)):
            p.add(f'<circle cx="{cx_}" cy="{cy_}" r="{mm(0.8)}" fill="none" stroke="#9aa3c8"/>')
    return pins_down(p, x + w / 2, y + h, list(order), mm(PITCH), tip if tip is not None else mm(3.5))


def module_rtc(p, x, y, optional=True, tip=None):
    w, h = mm(38), mm(22)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{mm(1)}" fill="{PCB_BLUE}" stroke="#0e2a50" stroke-dasharray="{"6 4" if optional else "none"}"/>')
    p.add(f'<circle cx="{x+w-mm(11)}" cy="{y+h/2-mm(1.2)}" r="{mm(9.5)}" fill="#dcdcdc" stroke="#8c8c8c" stroke-width="1.5"/>')
    p.text(x + w - mm(11), y + h / 2 + 1, "coin cell", 8, "#555", "middle")
    p.add(f'<rect x="{x+mm(3)}" y="{y+mm(4)}" width="{mm(8)}" height="{mm(5)}" rx="1" fill="#111" stroke="#444"/>')
    p.text(x + mm(7), y + mm(7.4), "DS3231", 6.5, "#ddd", "middle")
    out = {}
    for i, l in enumerate(["32K", "SQW", "SCL", "SDA", "VCC", "GND"]):
        px = x + mm(4.5) + i * mm(PITCH)
        t = tip if tip is not None else mm(3.5)
        p.add(f'<line x1="{px}" y1="{y+h}" x2="{px}" y2="{y+h+t}" stroke="#8d8d8d" stroke-width="3"/>')
        p.text(px, y + h - mm(0.8), l, 6.5, "#fff", "middle", 700)
        out[l] = (px, y + h + t)
    return out


def jumper(p, x, y, color, length_mm=40, ff=False):
    """ff=False: male both ends (a pin sticks out of each). ff=True: male-to-female
    (pin on the left, hollow socket on the right)."""
    L = mm(length_mm)
    end = mm(2.2)
    p.add(f'<rect x="{x}" y="{y-3.5}" width="{end}" height="7" rx="1.5" fill="#222"/>')
    p.add(f'<line x1="{x-6}" y1="{y}" x2="{x}" y2="{y}" stroke="#aaa" stroke-width="1.5"/>')
    if ff:
        p.add(f'<rect x="{x+L-end}" y="{y-4}" width="{end}" height="8" rx="1.5" fill="#333"/><rect x="{x+L-6}" y="{y-1.5}" width="4" height="3" fill="#999"/>')
    else:
        p.add(f'<rect x="{x+L-end}" y="{y-3.5}" width="{end}" height="7" rx="1.5" fill="#222"/>')
        p.add(f'<line x1="{x+L}" y1="{y}" x2="{x+L+6}" y2="{y}" stroke="#aaa" stroke-width="1.5"/>')
    p.add(f'<line x1="{x+end}" y1="{y}" x2="{x+L-end}" y2="{y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')


def cable(p, x, y, length_mm=30):
    L = mm(length_mm)
    p.add(f'<rect x="{x}" y="{y-mm(1.4)}" width="{mm(6)}" height="{mm(2.8)}" rx="{mm(1.2)}" fill="#cfcfcf" stroke="#7a7a7a"/>')
    p.add(f'<path d="M {x+mm(6)} {y} C {x+L*0.4} {y-mm(10)} {x+L*0.6} {y+mm(10)} {x+L-mm(6)} {y}" stroke="#2b2b2b" stroke-width="5" fill="none"/>')
    p.add(f'<rect x="{x+L-mm(6)}" y="{y-mm(1.4)}" width="{mm(6)}" height="{mm(2.8)}" rx="{mm(1.2)}" fill="#cfcfcf" stroke="#7a7a7a"/>')


def sdcard(p, x, y):
    w, h = mm(11), mm(15)
    p.add(f'<path d="M {x} {y+mm(2)} L {x+mm(2)} {y} L {x+w} {y} L {x+w} {y+h} L {x} {y+h} Z" fill="#232323" stroke="#555"/>')
    p.text(x + w / 2, y + h / 2 + 3, "32 GB", 8, "#eee", "middle")


# ------------------------------------------------------------------- shared pages
def page_choose():
    p = Page("Which kit do you have?", "Two builds, one station. The difference is one part: a breadboard. Check the bag, pick a column, and follow only that kit's pages from here.")
    for i, (tag, col, title, rows) in enumerate((
        ("Kit A", "#1d6fd8", "Kit A: breadboard", [
            "A small plastic slab full of holes is in the bag.",
            "Sensor and screen run at the same time, joined",
            "through the breadboard. Twelve jumper wires with",
            "a pin at both ends (male to male).",
            "",
            "The US workshop kit and the UK bench.",
            "About 25 minutes to a working station."]),
        ("Kit B", "#7a4fb0", "Kit B: direct, no breadboard", [
            "No breadboard in the bag.",
            "Four wires go straight from the board's sockets",
            "to one module. Sensor first; then the screen, on",
            "its own. The wires need a pin at one end and a",
            "socket at the other (male to female).",
            "",
            "For any kit without a breadboard. Works",
            "anywhere. About 15 minutes."]))):
        x = 60 + i * 680
        p.add(f'<rect x="{x}" y="120" width="620" height="780" rx="16" fill="#fafafa" stroke="{col}" stroke-width="3"/>')
        p.add(f'<rect x="{x+24}" y="144" width="110" height="34" rx="17" fill="{col}"/>')
        p.text(x + 79, 167, tag, 15, "#fff", "middle", 700)
        p.text(x + 150, 168, title, 22, INK, weight=700)
        p.lines(x + 24, 220, rows, 15, INK, 24)
        if i == 0:
            MiniBreadboard(p, x + 60, 560)
            module_bme(p, x + 60 + mm(2.2) + mm(PITCH) * 1.5 - mm(11.5) / 2, 560 - mm(3.5) - mm(15))
            for k in range(4):
                jumper(p, x + 440, 590 + k * 30, (RED, BLK, BLU, YEL)[k], 14)
            p.text(x + 440, 570, "male to male", 12, MUTE)
            p.text(x + 60, 560 + mm(35) + 40, "modules sit in the breadboard;", 13, MUTE)
            p.text(x + 60, 560 + mm(35) + 60, "four columns become the shared wires", 13, MUTE)
        else:
            b = PB2(p, x + 60, 640, usb_left=True, hot=HOT, numbers=False)
            tips = module_bme(p, x + 60 + mm(28) - mm(5.75) + mm(10), 440)
            for pin, lab, c in ((14, "VIN", RED), (15, "GND", BLK), (26, "SDA", BLU), (28, "SCL", YEL)):
                (sx, sy), (tx, ty) = b.pin_xy(pin), tips[lab]
                p.add(f'<path d="M {sx} {sy} C {sx} {sy-50} {tx} {ty+50} {tx} {ty}" stroke="#fff" stroke-width="8" fill="none" opacity="0.9"/>')
                p.add(f'<path d="M {sx} {sy} C {sx} {sy-50} {tx} {ty+50} {tx} {ty}" stroke="{c}" stroke-width="4.5" fill="none"/>')
            for k in range(4):
                jumper(p, x + 470, 610 + k * 30, (RED, BLK, BLU, YEL)[k], 14, ff=True)
            p.text(x + 470, 590, "male to female", 12, MUTE)
            p.text(x + 24, 420, "one module at a time, wired straight from the board's sockets", 13, MUTE)
    p.text(40, PAGE_H - 30, "Same board, same four pins, same software, same checks. Only the joining differs. A Kit B bench becomes a Kit A bench the day a breadboard turns up.", 13, INK)
    p.save("choose-kit.svg")


def page_board_pins():
    p = Page("Where the four pins are", "Board held with the sockets facing you and the USB-C port on the right, as BeagleBoard photographs it. On your table it is turned round; the numbers are the same.", h=900)
    b = PB2(p, 80, 120, usb_left=False, hot=HOT, scale=SCALE * 1.75)
    x1, y1 = b.pin_xy(1)
    p.add(f'<circle cx="{x1}" cy="{y1}" r="19" fill="none" stroke="{RED}" stroke-width="3"/>')
    p.text(x1 + 10, y1 + 64, "P1.1 is 5 V. Nothing ever goes in here.", 14, RED, "end", 700)
    zx, zy, zp = 80, 720, 42
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
    lx = 920
    p.text(lx, 150, "The four we use", 17, INK, weight=700)
    for i, (pin, what, where) in enumerate(((14, "3.3 V out", "column 7, inner row"), (15, "ground", "column 8, outer row"), (26, "SDA, data", "column 13, inner row"), (28, "SCL, clock", "column 14, inner row"))):
        y = 192 + i * 64
        p.add(f'<rect x="{lx}" y="{y-20}" width="30" height="30" rx="4" fill="{HOT[pin]}"/>')
        p.text(lx + 15, y + 1, str(pin), 13, "#fff" if HOT[pin] != YEL else INK, "middle", 700)
        p.text(lx + 44, y - 4, f"P1.{pin}  {NAMES[pin]}", 15, INK, weight=700)
        p.text(lx + 44, y + 16, f"{what}. {where}, from the USB-C end.", 13, MUTE)
    p.lines(lx, 480, ["Trust the numbers printed on the board over", "this picture. Find the printed 1 and 2 at the"], 13, INK, 18, 700)
    p.lines(lx, 516, ["USB-C end of P1 and the 35 and 36 at the far", "end. If they are there, the columns are right."], 13, MUTE, 18)
    p.save("board-pins.svg")


def page_wiring():
    p = Page("The four wires, as a schematic", "The same four wires for every module: power, ground, data, clock. This is the whole circuit, in either kit.")
    b = PB2(p, 60, 130, usb_left=False, hot=HOT, scale=SCALE * 1.2)
    bw = 56 * SCALE * 1.2
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
    p.text((rx[RED] + rx[YEL]) / 2, bot + 24, "Kit A: four breadboard columns.  Kit B: four wires, one module", 12, MUTE, "middle")

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
    block(x, y, "DS3231 real time clock  (optional, Kit A only)", "keeps time on a coin cell when the board is off",
          [("VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU), ("32K, SQW: leave open", None)],
          "answers at 0x68. 0x57 is the EEPROM on the same module", optional=True)
    p.save("wiring.svg")


# ------------------------------------------------------------------- Kit A
A_SENSOR, A_OLED = 1, 9                      # first pin column of each module
A_NET = {RED: 14, BLK: 15, BLU: 16, YEL: 17}  # the four shared columns, top half, board end
A_ROW = {"board": "h", "sensor": "f", "screen": "g"}   # which hole of a shared column each wire uses
A_STEP_TITLES = {1: "Kit A, step 1 of 4: seat the modules", 2: "Kit A, step 2 of 4: four wires from the board", 3: "Kit A, step 3 of 4: the sensor's four wires", 4: "Kit A, step 4 of 4: the screen's four wires"}
A_STEP_SUBS = {1: "Sensor pins in row j, columns 1 to 4. Screen pins in row j, columns 9 to 12. Bodies hang off the top edge. USB cable still in the bag.",
               2: "The four columns nearest the board become the shared wires: 14 is 3.3 V, 15 is ground, 16 is SDA, 17 is SCL. Red P1.14 to 14, black P1.15 to 15, blue P1.26 to 16, yellow P1.28 to 17.",
               3: "From the sensor's columns to the shared columns, all in row f: VIN to 14, GND to 15, SDA to 16, SCL to 17. Read the sensor's letters before each wire.",
               4: "Same for the screen, in YOUR screen's pin order, ending in row g: VCC to 14, GND to 15, SDA to 16, SCL to 17. Then check every wire out loud."}


def page_kit_A():
    p = Page("Kit A: what is in the bag", "Tip everything out and match each thing to a picture. Everything is drawn at the same scale as every later picture.", h=1080, tag="Kit A: breadboard")
    PB2(p, 60, 130); p.callout(34, 136, 1)
    p.text(60, 130 + mm(35) + 30, "PocketBeagle 2", 17, INK, weight=700)
    p.lines(60, 130 + mm(35) + 52, ["The computer. Two black strips of sockets (P1, P2) along the long edges,", "tiny numbers at the strip ends. Hold it by the edges. The side with the", "microSD slot and the dog logo is the side you use."], 13, MUTE, 18)
    MiniBreadboard(p, 600, 140); p.callout(574, 146, 2)
    p.text(600, 140 + mm(35) + 44, "Mini breadboard, 170 holes", 17, INK, weight=700)
    p.lines(600, 140 + mm(35) + 66, ["A small plastic slab, 17 columns by 10 rows, with a groove across the middle.", "No red or blue power lines on this size; that is expected."], 13, MUTE, 18)
    cable(p, 1060, 160, 28); p.callout(1034, 160, 3)
    p.text(1060, 200, "USB-C cable", 17, INK, weight=700)
    p.lines(1060, 222, ["Must be a data cable. A charge-only", "cable looks identical and is the most", "common reason nothing works."], 13, MUTE, 18)
    sdcard(p, 1060, 300); p.callout(1034, 310, 4)
    p.text(1060 + mm(11) + 14, 316, "microSD card", 17, INK, weight=700)
    p.lines(1060 + mm(11) + 14, 338, ["8 GB or more. Holds the", "whole operating system."], 13, MUTE, 18)
    y0 = 600
    module_bme(p, 70, y0); p.callout(44, y0 + 6, 5)
    p.text(40, y0 + mm(15) + 50, "BME280 sensor", 17, INK, weight=700)
    p.lines(40, y0 + mm(15) + 72, ["Fingernail sized, purple or blue, four pins", "(a few have six): VIN or VCC, GND, SCL, SDA", "in tiny letters. The small metal can is the", "sensor itself. If the pins are loose in the", "bag instead of soldered on, stop: that is", "a different job."], 13, MUTE, 18)
    module_oled(p, 340, y0); p.callout(314, y0 + 6, 6)
    p.text(340, y0 + mm(27) + 50, "OLED screen (SSD1306, 0.96 inch)", 17, INK, weight=700)
    p.lines(340, y0 + mm(27) + 72, ["A square board with a dark glass window and four pins on", "one edge: VCC, GND, SCL, SDA. The order of VCC and GND"], 13, MUTE, 18)
    p.text(340, y0 + mm(27) + 108, "differs between makers. Read yours now and write it down.", 13, INK, weight=700)
    p.lines(340, y0 + mm(27) + 126, ["Getting those two backwards is the one mistake in this", "guide that kills a part instantly."], 13, MUTE, 18)
    module_rtc(p, 760, y0 + 20); p.callout(734, y0 + 26, 7)
    p.text(760, y0 + mm(22) + 70, "DS3231 clock (optional)", 17, INK, weight=700)
    p.lines(760, y0 + mm(22) + 92, ["The one with the round coin cell holder. Six pins;", "only SCL, SDA, VCC, GND are used. Leave it in the", "bag on your first build. No battery until you have", "read the battery note in HARDWARE.md."], 13, MUTE, 18)
    jx = 1090
    p.callout(jx - 26, y0 + 6, 8)
    p.text(jx, y0 + 12, "Jumper wires, male to male", 17, INK, weight=700)
    p.lines(jx, y0 + 34, ["A pin at both ends. 12 needed,", "16 with the clock."], 13, MUTE, 18)
    for i, c in enumerate((RED, BLK, BLU, YEL)):
        jumper(p, jx, y0 + 80 + i * 26, c, 20)
        p.text(jx + mm(20) + 14, y0 + 85 + i * 26, LABEL[c], 13, INK)
    p.lines(jx, y0 + 200, ["Any four colours work if you use", "them the same way throughout."], 13, MUTE, 18)
    p.text(40, 1080 - 30, "Not in the bag and not needed: a monitor, keyboard or power supply for the board. Your laptop is all three, through the USB-C cable.", 13, INK)
    p.save("kit-A.svg")


def page_mat_A():
    p = Page("Kit A: lay it out like this before you start", "This is the arrangement every later picture uses. You sit at the bottom edge. Cable and card stay where they are until Parts 3 and 4.", h=1080, tag="Kit A: breadboard")
    mx, my, mw, mh = 60, 105, 1280, 950
    p.add(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="10" fill="#fcfcfc" stroke="#c4c4c4" stroke-dasharray="10 7" stroke-width="2"/>')
    p.text(mx + mw - 14, my + mh - 12, "your table, seen from above", 12, MUTE, "end")

    def zone(x, y, w, h, n, title):
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#eef3fa" stroke="#9db4d3" stroke-width="1.5"/>')
        p.callout(x + 24, y + 24, n); p.text(x + 48, y + 30, title, 15, INK, weight=700)

    z1h = 300
    zone(mx + 15, my + 15, 430, z1h, 1, "Modules, pins toward you")
    module_bme(p, mx + 60, my + 80); p.text(mx + 60 + mm(5.75), my + 80 + mm(15) + 44, "sensor", 12, MUTE, "middle")
    module_oled(p, mx + 200, my + 62); p.text(mx + 200 + mm(13.5), my + 62 + mm(27) + 44, "screen", 12, MUTE, "middle")
    p.text(mx + 35, my + z1h - 34, "Screen pin order, left to right:  ____  ____  ____  ____", 13, INK)
    p.text(mx + 35, my + z1h - 12, "Clock stays in the bag today.", 12, MUTE)
    zone(mx + 460, my + 15, 500, z1h, 2, "Jumpers in four rows, by colour")
    for i, (c, n) in enumerate([(RED, "3 red"), (BLK, "3 black"), (BLU, "3 blue"), (YEL, "3 yellow")]):
        for k in range(3):
            jumper(p, mx + 500 + k * 130, my + 90 + i * 40, c, 13)
        p.text(mx + 900, my + 95 + i * 40, n, 13, INK)
    p.text(mx + 480, my + z1h - 12, "Count them now. Hunting for a missing wire at step 3 costs ten minutes of doubt.", 12, MUTE)
    zone(mx + 975, my + 15, 290, z1h, 3, "Not yet")
    sdcard(p, mx + 1010, my + 70); p.text(mx + 1010 + mm(11) + 14, my + 96, "card: Part 3", 13, INK)
    cable(p, mx + 1000, my + 220, 26); p.text(mx + 1000, my + 256, "cable: Part 4, not before", 13, INK)
    p.text(mx + 1000, my + z1h - 12, "Laptop closed, to one side.", 12, MUTE)
    z4y = my + 15 + z1h + 12; z4h = 330
    zone(mx + 15, z4y, 1250, z4h, 4, "Breadboard, the long way across, 4 cm below the modules")
    MiniBreadboard(p, mx + 480, z4y + 40)
    p.lines(mx + 35, z4y + 70, ["Column numbers run left to right,", "1 to 17. The groove across the", "middle splits each column into a", "top half (rows f to j) and a bottom", "half (rows a to e). They are not", "joined to each other."], 13, INK, 20)
    p.lines(mx + 900, z4y + 70, ["Modules go along the top edge with", "their pins in row j. Four columns in", "the middle, 5 to 8, become the shared", "wires. Nothing goes in the bottom half", "in this build."], 13, MUTE, 20)
    z5y = z4y + z4h + 12; z5h = my + mh - 15 - z5y
    zone(mx + 15, z5y, 1250, z5h, 5, "PocketBeagle 2, sockets up, USB-C port to the LEFT")
    PB2(p, mx + 420, z5y + 20, usb_left=True)
    p.lines(mx + 900, z5y + 60, ["Turned so P1 is the strip nearest the", "breadboard. Pin 1 is then at the left end", "of P1, by the USB-C port."], 13, INK, 20)
    p.lines(mx + 900, z5y + 130, ["Find the tiny printed 1 and 2 there", "before going on."], 13, INK, 20, 700)
    p.lines(mx + 900, z5y + 180, ["Every wire that leaves P1 goes straight", "up into the breadboard."], 13, MUTE, 20)
    p.save("layout-mat-A.svg")


def page_step_A(step):
    global SCALE
    saved = SCALE; SCALE = 9.0          # this page is drawn larger; the mini board is small
    p = Page(A_STEP_TITLES[step], A_STEP_SUBS[step], tag="Kit A: breadboard")
    bby = 110 + mm(27) + mm(3.5) + 24
    bb = MiniBreadboard(p, 120, bby)
    cx = bb.col_x
    yj = bb.row_y("j")
    tip = mm(3.5)
    module_bme(p, cx(A_SENSOR) + mm(PITCH) * 1.5 - mm(11.5) / 2, yj - tip - mm(15))
    module_oled(p, cx(A_OLED) + mm(PITCH) * 1.5 - mm(27) / 2, yj - tip - mm(27))
    p.text(cx(A_SENSOR + 1.5), yj - tip - mm(15) - 12, "sensor", 13, INK, "middle", 700)
    p.text(cx(A_OLED + 1.5), yj - tip - mm(27) - 12, "screen: use YOUR pin order", 13, INK, "middle", 700)
    if step >= 2:
        for c, col in A_NET.items():
            p.add(f'<rect x="{cx(col)-mm(1.4)}" y="{yj-mm(1.4)}" width="{mm(2.8)}" height="{bb.row_y("f")-yj+mm(2.8)}" rx="3" fill="{c}" opacity="0.16"/>')
            p.text(cx(col), yj - mm(2.2), str(col), 11, c, "middle", 700)
    # the board sits to the right, turned so P1 is its top strip and pin 1 is nearest the breadboard
    bx = 120 + mm(45) + 150
    yb = bby + mm(35) - mm(35) + 40
    board = PB2(p, bx, yb, usb_left=True, hot=HOT if step >= 2 else None)
    off = mm(PITCH) / 2
    if step >= 2:
        row = bb.row_y(A_ROW["board"])
        half = mm(PITCH) / 2
        # lanes run BETWEEN hole rows so no wire looks plugged into a column it only passes
        lanes = {14: bb.row_y("i") + half, 15: bb.row_y("h") + half, 26: bb.row_y("j") + half, 28: bb.row_y("g") + half}
        for k, (pin, c) in enumerate(HOT.items()):
            x, y = board.pin_xy(pin); col = A_NET[c]
            lane = lanes[pin]
            p.wire([(x, y), (x, yb - 30 - k * 10), (bx - 40 - k * 10, yb - 30 - k * 10), (bx - 40 - k * 10, lane), (cx(col) + off, lane), (cx(col) + off, row + (6 if lane < row else -6)), (cx(col), row)], c)
        for pin, dx in ((14, -12), (15, 12), (26, -12), (28, 12)):
            x, y = board.pin_xy(pin)
            p.text(x + dx, y + 30 if pin in (15, 28) else y + 44, f"P1.{pin}", 10, "#fff", "middle", 700)
    def module_dips(c0, order, end_row):
        # from row f of the module's column, dipping down through the empty bottom half,
        # up into the shared column. longer reach, deeper dip, so the wires never overlap.
        for i, c in enumerate(order):
            col = c0 + i; net = A_NET[c]
            a = (cx(col), bb.row_y("f")); b = (cx(net), bb.row_y(end_row))
            depth = mm(14) + (net - col) * mm(0.9) + (0 if end_row == "f" else mm(3))
            p.arc(a, b, c, lift=-depth)
    if step >= 3:
        module_dips(A_SENSOR, [RED, BLK, YEL, BLU], A_ROW["sensor"])
    if step >= 4:
        module_dips(A_OLED, [BLK, RED, YEL, BLU], A_ROW["screen"])
    notes = {1: ["Press each module in firmly and evenly; it takes more force than you expect. Pins in row j, one per column. Nothing goes in the bottom half of the board.",
                 "The bodies hang off the top edge. Columns 14 to 17, nearest the computer, stay empty: they become the four shared wires in step 2."],
             2: ["Each shared column is one wire inside the breadboard, five holes long. The board's wire, the sensor's wire and the screen's wire will each use one hole of it.",
                 "Say it out loud: red leaves 14 and arrives at column 14. Black leaves 15 and arrives at 15. Blue leaves 26 and arrives at 16. Yellow leaves 28 and arrives at 17."],
             3: ["Sensor wires start in row f under each sensor pin and end in row f of a shared column. They swing across the empty bottom half; they touch the board only at their ends.",
                 "Follow each one with a finger back to the sensor and read the letter at that column: red must end at VIN, black at GND. VIN and GND swapped kills the sensor at power on."],
             4: ["Screen wires start in row f under each screen pin and end in row g of a shared column, in the pin order you wrote down for YOUR screen.",
                 "Twelve wires in total. Nothing in P1.1. No bare pins touching. That is the whole circuit."]}
    p.lines(40, PAGE_H - 44, notes[step], 13, INK, 20)
    p.legend(1200, 150 + mm(35) + 220)
    p.lines(1188, 150 + mm(35) + 340, ["board turned so P1 is its top", "strip, pin 1 nearest the", "breadboard, USB-C on the left."], 11, MUTE, 16)
    SCALE = saved
    p.save(f"bench-A-step{step}.svg")


# ------------------------------------------------------------------- Kit B
B_STEP_TITLES = {1: "Kit B, step 1 of 2: the sensor, wired straight to the board", 2: "Kit B, step 2 of 2: the screen, on its own"}
B_STEP_SUBS = {1: "Four male-to-female wires, pin end in the board, socket end on the module. Red P1.14 to VIN, black P1.15 to GND, blue P1.26 to SDA, yellow P1.28 to SCL. USB cable still in the bag.",
               2: "Unplug the USB. Move the same four wires to the screen, in YOUR screen's pin order: red to VCC, black to GND, blue to SDA, yellow to SCL."}


def page_kit_B():
    p = Page("Kit B: what is in the bag", "No breadboard in this kit. Tip everything out and match each thing to a picture. Everything is drawn at the same scale as every later picture.", h=1080, tag="Kit B: direct")
    PB2(p, 60, 130); p.callout(34, 136, 1)
    p.text(60, 130 + mm(35) + 30, "PocketBeagle 2", 17, INK, weight=700)
    p.lines(60, 130 + mm(35) + 52, ["The computer. Two black strips of sockets (P1, P2) along the long edges,", "tiny numbers at the strip ends. Hold it by the edges. The side with the", "microSD slot and the dog logo is the side you use."], 13, MUTE, 18)
    cable(p, 640, 160, 28); p.callout(614, 160, 2)
    p.text(640, 200, "USB-C cable", 17, INK, weight=700)
    p.lines(640, 222, ["Must be a data cable. A charge-only", "cable looks identical and is the most", "common reason nothing works."], 13, MUTE, 18)
    sdcard(p, 980, 150); p.callout(954, 160, 3)
    p.text(980 + mm(11) + 14, 166, "microSD card", 17, INK, weight=700)
    p.lines(980 + mm(11) + 14, 188, ["8 GB or more. Holds the", "whole operating system."], 13, MUTE, 18)
    y0 = 520
    module_bme(p, 70, y0); p.callout(44, y0 + 6, 4)
    p.text(40, y0 + mm(15) + 50, "BME280 sensor", 17, INK, weight=700)
    p.lines(40, y0 + mm(15) + 72, ["Fingernail sized, purple or blue, four pins", "(a few have six): VIN or VCC, GND, SCL, SDA", "in tiny letters. The small metal can is the", "sensor itself. If the pins are loose in the", "bag instead of soldered on, stop: that is", "a different job."], 13, MUTE, 18)
    module_oled(p, 340, y0); p.callout(314, y0 + 6, 5)
    p.text(340, y0 + mm(27) + 50, "OLED screen (SSD1306, 0.96 inch)", 17, INK, weight=700)
    p.lines(340, y0 + mm(27) + 72, ["A square board with a dark glass window and four pins on", "one edge: VCC, GND, SCL, SDA. The order of VCC and GND"], 13, MUTE, 18)
    p.text(340, y0 + mm(27) + 108, "differs between makers. Read yours now and write it down.", 13, INK, weight=700)
    p.lines(340, y0 + mm(27) + 126, ["Getting those two backwards is the one mistake in this", "guide that kills a part instantly."], 13, MUTE, 18)
    jx = 820
    p.callout(jx - 26, y0 + 6, 6)
    p.text(jx, y0 + 12, "Jumper wires, male to female", 17, INK, weight=700)
    p.lines(jx, y0 + 34, ["A pin at one end, a socket at the other. Four", "needed. The pin end goes into the board's socket;", "the socket end slides over the module's pin.", "", "Male-to-male wires will not reach the module.", "Female-to-female wires will not reach the board."], 13, MUTE, 18)
    for i, c in enumerate((RED, BLK, BLU, YEL)):
        jumper(p, jx, y0 + 140 + i * 26, c, 20, ff=True)
        p.text(jx + mm(20) + 14, y0 + 145 + i * 26, LABEL[c], 13, INK)
    p.lines(jx, y0 + 260, ["No male-to-female wires? A male-to-male wire plus a", "female-to-female wire, joined end to end, does the same job."], 13, INK, 18)
    p.text(40, 1080 - 30, "Not in the bag and not needed: a monitor, keyboard or power supply for the board. Your laptop is all three, through the USB-C cable.", 13, INK)
    p.save("kit-B.svg")


def page_mat_B():
    p = Page("Kit B: lay it out like this before you start", "This is the arrangement every later picture uses. You sit at the bottom edge. Cable and card stay where they are until Parts 3 and 4.", h=1080, tag="Kit B: direct")
    mx, my, mw, mh = 60, 105, 1280, 950
    p.add(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="10" fill="#fcfcfc" stroke="#c4c4c4" stroke-dasharray="10 7" stroke-width="2"/>')
    p.text(mx + mw - 14, my + mh - 12, "your table, seen from above", 12, MUTE, "end")

    def zone(x, y, w, h, n, title):
        p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#f3effa" stroke="#b9a6d6" stroke-width="1.5"/>')
        p.callout(x + 24, y + 24, n, "#7a4fb0"); p.text(x + 48, y + 30, title, 15, INK, weight=700)

    z1h = 300
    zone(mx + 15, my + 15, 430, z1h, 1, "Modules, pins toward you")
    module_bme(p, mx + 60, my + 80); p.text(mx + 60 + mm(5.75), my + 80 + mm(15) + 44, "sensor: first", 12, MUTE, "middle")
    module_oled(p, mx + 200, my + 62); p.text(mx + 200 + mm(13.5), my + 62 + mm(27) + 44, "screen: second", 12, MUTE, "middle")
    p.text(mx + 35, my + z1h - 34, "Screen pin order, left to right:  ____  ____  ____  ____", 13, INK)
    zone(mx + 460, my + 15, 500, z1h, 2, "Four wires, one of each colour")
    for i, c in enumerate((RED, BLK, BLU, YEL)):
        jumper(p, mx + 520, my + 90 + i * 40, c, 30, ff=True)
        p.text(mx + 520 + mm(30) + 20, my + 95 + i * 40, LABEL[c], 13, INK)
    p.text(mx + 480, my + z1h - 12, "Pin end into the board's socket. Socket end over the module's pin.", 12, MUTE)
    zone(mx + 975, my + 15, 290, z1h, 3, "Not yet")
    sdcard(p, mx + 1010, my + 70); p.text(mx + 1010 + mm(11) + 14, my + 96, "card: Part 3", 13, INK)
    cable(p, mx + 1000, my + 220, 26); p.text(mx + 1000, my + 256, "cable: Part 4, not before", 13, INK)
    p.text(mx + 1000, my + z1h - 12, "Laptop closed, to one side.", 12, MUTE)
    z5y = my + 15 + z1h + 12; z5h = my + mh - 15 - z5y
    zone(mx + 15, z5y, 1250, z5h, 4, "PocketBeagle 2, sockets up, USB-C port to the LEFT, the sensor 5 cm above it")
    PB2(p, mx + 420, z5y + 200, usb_left=True)
    module_bme(p, mx + 420 + mm(28) - mm(5.75), z5y + 60)
    p.lines(mx + 900, z5y + 80, ["P1 is the top strip, nearest the module.", "Pin 1 is at the left end of P1, by the", "USB-C port."], 13, INK, 20)
    p.lines(mx + 900, z5y + 150, ["Find the tiny printed 1 and 2 there", "before going on."], 13, INK, 20, 700)
    p.lines(mx + 900, z5y + 200, ["The module just sits on the table above", "the board, pins toward it. Four short wires", "join them. Nothing to press into anything", "except the wire ends."], 13, MUTE, 20)
    p.save("layout-mat-B.svg")


def page_step_B(step):
    p = Page(B_STEP_TITLES[step], B_STEP_SUBS[step], tag="Kit B: direct")
    yb = 540
    board = PB2(p, 420, yb, usb_left=True, hot=HOT)
    if step == 1:
        tips = module_bme(p, 420 + mm(28) - mm(5.75) + mm(14), 300)
        order = (("VIN", RED, 14), ("GND", BLK, 15), ("SDA", BLU, 26), ("SCL", YEL, 28))
        p.text(420 + mm(28) + mm(14), 300 - 14, "sensor", 13, INK, "middle", 700)
    else:
        tips = module_oled(p, 420 + mm(28) - mm(13.5) + mm(6), 300 - mm(12))
        order = (("VCC", RED, 14), ("GND", BLK, 15), ("SDA", BLU, 26), ("SCL", YEL, 28))
        p.text(420 + mm(28) + mm(6), 300 - mm(12) - 14, "screen: use YOUR pin order", 13, INK, "middle", 700)
    for lab, c, pin in order:
        (sx, sy), (tx, ty) = board.pin_xy(pin), tips[lab]
        p.add(f'<path d="M {sx} {sy} C {sx} {sy-110} {tx} {ty+110} {tx} {ty}" stroke="#fff" stroke-width="9" fill="none" opacity="0.95"/>')
        p.add(f'<path d="M {sx} {sy} C {sx} {sy-110} {tx} {ty+110} {tx} {ty}" stroke="{c}" stroke-width="5" fill="none"/>')
        p.add(f'<circle cx="{sx}" cy="{sy}" r="6.5" fill="{c}" stroke="#fff" stroke-width="2"/><circle cx="{tx}" cy="{ty}" r="6.5" fill="{c}" stroke="#fff" stroke-width="2"/>')
    for pin, dx in ((14, -12), (15, 12), (26, -12), (28, 12)):
        x, y = board.pin_xy(pin)
        p.text(x + dx, y + 30 if pin in (15, 28) else y + 46, f"P1.{pin}", 10, "#fff", "middle", 700)
    notes = {1: ["Say it out loud: red leaves 14 and arrives at VIN. Black leaves 15 and arrives at GND. Blue leaves 26 and arrives at SDA. Yellow leaves 28 and arrives at SCL.",
                 "Nothing in P1.1. Then Part 3 (the card) and Part 4 (power). The sensor alone is a working station: readings come to your laptop with sws-live."],
             2: ["Only after the sensor has answered in Part 5. USB out first; never move a wire with power on. The screen alone shows the pages with -- where readings would be.",
                 "A screen and a sensor together need a breadboard (Kit A). Until one arrives, this proves both parts and all four pins, which is most of the work."]}
    p.lines(40, PAGE_H - 44, notes[step], 13, INK, 20)
    p.legend(1200, 150)
    p.lines(1188, 290, ["board turned so P1 faces the", "module: USB-C on the left,", "pin 1 at the left end of P1."], 11, MUTE, 16)
    p.save(f"bench-B-step{step}.svg")


# ------------------------------------------------------------------- print
def print_pdf(name, pages):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed; skipping", name); return
    html = ["<html><head><meta charset='utf-8'><style>@page{size:A4 landscape;margin:8mm} html,body{margin:0;padding:0} .pg{width:281mm;height:194mm;display:flex;align-items:center;justify-content:center;overflow:hidden} .pg+.pg{page-break-before:always} img{max-width:281mm;max-height:194mm;width:auto;height:auto}</style></head><body>"]
    for n in pages:
        html.append(f"<div class='pg'><img src='../{n}.svg'></div>")
    html.append("</body></html>")
    idx = os.path.join(PRINT, "sheets.html")
    with open(idx, "w") as f: f.write("".join(html))
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None)
        pg = b.new_page(); pg.goto("file://" + idx)
        pg.pdf(path=os.path.join(PRINT, name), format="A4", landscape=True, print_background=True,
               margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"})
        b.close()
    os.remove(idx)
    print("wrote print/" + name)


if __name__ == "__main__":
    page_choose(); page_board_pins(); page_wiring()
    page_kit_A(); page_mat_A()
    for i in (1, 2, 3, 4): page_step_A(i)
    page_kit_B(); page_mat_B()
    for i in (1, 2): page_step_B(i)
    if "--print" in sys.argv:
        print_pdf("FIRST-BUILD-kit-A.pdf", ["choose-kit", "kit-A", "layout-mat-A", "board-pins", "bench-A-step1", "bench-A-step2", "bench-A-step3", "bench-A-step4", "wiring"])
        print_pdf("FIRST-BUILD-kit-B.pdf", ["choose-kit", "kit-B", "layout-mat-B", "board-pins", "bench-B-step1", "bench-B-step2", "wiring"])
