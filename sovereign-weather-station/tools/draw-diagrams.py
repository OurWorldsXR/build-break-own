#!/usr/bin/env python3
"""Draws every diagram in images/. Run it after any change; never hand-edit the SVGs.

    python3 tools/draw-diagrams.py

Facts the drawings rest on (see HARDWARE.md and WIRING.md for sources):
  PocketBeagle 2, header side = the side with the microSD slot and dog logo.
  Sockets up, USB-C to the right: P1 is the bottom strip, P2 the top.
  Pins 1/2 at the USB-C end, 35/36 at the far end. On P1 odd pins are the outer row.
  P1.14 VDD_3V3, P1.15 GND, P1.26 I2C2_SDA, P1.28 I2C2_SCL.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
os.makedirs(OUT, exist_ok=True)

# palette
RED, BLK, BLU, YEL = "#d7362e", "#1f1f1f", "#2f6fdb", "#e0a800"
INK, MUTE, PAPER = "#1b1b1b", "#6b6b6b", "#ffffff"
BOARD, BOARD_EDGE, SOCKET = "#233333", "#0d1717", "#050808"
BB, BB_EDGE = "#f6f2e4", "#c9c1a6"
FONT = 'font-family="Inter, Helvetica, Arial, sans-serif"'
NAMES = {14: "VDD_3V3", 15: "GND", 26: "I2C2_SDA", 28: "I2C2_SCL"}
HOT = {14: RED, 15: BLK, 26: BLU, 28: YEL}
LABEL = {RED: "3.3 V", BLK: "GND", BLU: "SDA", YEL: "SCL"}


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>',
                  f'<rect width="{w}" height="{h}" fill="{PAPER}"/>',
                  f'<text x="32" y="40" font-size="22" font-weight="700" fill="{INK}">{title}</text>']

    def add(self, s): self.o.append(s)

    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight=400, style=""):
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {style}>{s}</text>')

    def wire(self, pts, color, width=4, outline=True):
        d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
        if outline:
            self.add(f'<path d="{d}" stroke="#fff" stroke-width="{width+3}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        for x, y in (pts[0], pts[-1]):
            self.add(f'<circle cx="{x}" cy="{y}" r="{width+1}" fill="{color}" stroke="#fff" stroke-width="1.5"/>')

    def save(self, name):
        self.add("</svg>")
        with open(os.path.join(OUT, name), "w") as f:
            f.write("\n".join(self.o))
        print("wrote", name)


def legend(s, x, y, items):
    for i, (c, t) in enumerate(items):
        yy = y + i * 22
        s.add(f'<rect x="{x}" y="{yy-11}" width="30" height="8" rx="4" fill="{c}"/>')
        s.text(x + 40, yy, t, 12)


# --------------------------------------------------------------------------
# 1. wiring.svg: the logical schematic
# --------------------------------------------------------------------------
def draw_wiring():
    W, H = 1000, 740
    s = SVG(W, H, "Sovereign Weather Station: the four wires")
    s.text(32, 64, "PocketBeagle 2, P1 header. Every module gets the same four wires. 3.3 V only; never P1.1, which is 5 V.", 13, MUTE)
    bx, by, bw, bh = 40, 100, 236, 470
    s.add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="{BOARD}" stroke="{BOARD_EDGE}" stroke-width="2"/>')
    s.text(bx + bw / 2, by + 30, "PocketBeagle 2", 15, "#fff", "middle", 700)
    s.text(bx + bw / 2, by + 48, "P1 header, pins 13 to 30 drawn as a list", 11, "#cfd8d8", "middle")
    s.text(bx + bw / 2, by + 62, "(on the board they sit in two rows)", 11, "#cfd8d8", "middle")
    px, py0, dy = bx + bw - 30, by + 96, 20
    ypin = {}
    for i, n in enumerate(range(13, 31)):
        y = py0 + i * dy; ypin[n] = y
        c = HOT.get(n)
        s.add(f'<rect x="{px-7}" y="{y-7}" width="14" height="14" rx="2" fill="{c or SOCKET}" stroke="{"#fff" if c else "#4a5a5a"}" stroke-width="{1.5 if c else 1}"/>')
        s.text(px - 16, y + 4, f"P1.{n}" + (f"  {NAMES[n]}" if c else ""), 12 if c else 11, "#fff" if c else "#8a9a9a", "end", 700 if c else 400)
    rx = {RED: 336, BLK: 368, BLU: 400, YEL: 432}
    top, bot = 150, 700
    for c, x in rx.items():
        s.add(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="{c}" stroke-width="5" stroke-linecap="round"/>')
        s.text(x, top - 10, LABEL[c], 11, c, "middle", 700)
    for n, c in HOT.items():
        s.wire([(px + 7, ypin[n]), (rx[c], ypin[n])], c, 4, outline=False)
    s.text(384, 722, "breadboard: two rails and two shared columns", 11, MUTE, "middle")

    def module(x, y, title, sub, pins, addr, optional=False):
        w, h = 330, 46 + 22 * len(pins) + 30
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{"#fafafa" if optional else "#f3f6ff"}" stroke="{"#9a9a9a" if optional else "#3b4a6b"}" stroke-width="2" stroke-dasharray="{"7 5" if optional else "none"}"/>')
        s.text(x + 14, y + 22, title, 14, INK, weight=700)
        s.text(x + 14, y + 38, sub, 11, MUTE)
        for i, (lab, c) in enumerate(pins):
            yy = y + 60 + i * 22
            s.add(f'<rect x="{x+8}" y="{yy-7}" width="14" height="14" rx="2" fill="{c or "#fff"}" stroke="{INK if c else "#aaa"}"/>')
            s.text(x + 30, yy + 4, lab, 12, INK if c else "#999")
            if c:
                s.wire([(rx[c], yy), (x + 8, yy)], c, 4, outline=False)
        s.text(x + 14, y + h - 12, addr, 11, MUTE)
        return h
    y = 100
    y += module(500, y, "BME280 sensor", "temperature, pressure, humidity. 3.3 V logic",
                [("VIN / VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU), ("CSB  (leave open; 6-pin boards only)", None), ("SDO  (open = 0x76, tied to 3V3 = 0x77)", None)],
                "answers at 0x76 or 0x77. chip ID 0x60 = BME280, 0x58 = BMP280") + 14
    y += module(500, y, "SSD1306 OLED, 128 x 64, I2C", "read the silkscreen: VCC and GND order varies by vendor",
                [("VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU)], "answers at 0x3C") + 14
    module(500, y, "DS3231 real time clock  (optional)", "keeps time on a coin cell when the board is off",
           [("VCC", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU), ("32K, SQW  (leave open)", None)],
           "answers at 0x68. 0x57 is the EEPROM on the same module", optional=True)
    s.save("wiring.svg")


# --------------------------------------------------------------------------
# 2. board-pins.svg: the board, header side up, with a zoomed strip of P1
# --------------------------------------------------------------------------
def draw_board():
    W, H = 1160, 760
    s = SVG(W, H, "Where the four pins are")
    s.text(32, 64, "Hold the board with the socket strips facing you and the USB-C port on your right. You are looking at the side with the microSD slot and the dog logo.", 13, MUTE)
    bx, by, bw, bh = 120, 100, 880, 400
    s.add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="72" fill="{BOARD}" stroke="{BOARD_EDGE}" stroke-width="2"/>')
    s.add(f'<rect x="{bx+bw-14}" y="{by+bh/2-30}" width="30" height="60" rx="8" fill="#c8c8c8" stroke="#777"/>')
    s.text(bx + bw + 28, by + bh / 2 + 4, "USB-C", 12, INK, weight=700)
    s.add(f'<rect x="{bx-14}" y="{by+bh/2-70}" width="26" height="38" rx="3" fill="#e6e6e6" stroke="#777"/>')
    s.text(bx - 22, by + bh / 2 - 80, "UART (not used)", 11, MUTE, "end")
    s.add(f'<rect x="{bx+bw-240}" y="{by+bh/2-46}" width="124" height="92" rx="6" fill="#a7b3b3" stroke="#666"/>')
    s.text(bx + bw - 178, by + bh / 2 + 4, "microSD", 11, "#123", "middle")
    s.text(bx + bw / 2 - 90, by + bh / 2 + 6, "beagleboard.org", 13, "#c9d3d3", style='font-style="italic"')
    pitch = 45; x0 = bx + bw - 62
    def strip(name, yout, yin, odd_outer, hot):
        for k in range(1, 19):
            x = x0 - (k - 1) * pitch
            odd, even = 2 * k - 1, 2 * k
            for pin, y in ((odd, yout if odd_outer else yin), (even, yin if odd_outer else yout)):
                c = hot.get(pin)
                s.add(f'<rect x="{x-9}" y="{y-9}" width="18" height="18" rx="2" fill="{c or SOCKET}" stroke="{"#fff" if c else "#4a5a5a"}" stroke-width="{2 if c else 1}"/>')
                if c:
                    s.text(x, y + 5, str(pin), 10, "#fff" if c != YEL else INK, "middle", 700)
        s.text(x0 + 34, (yout + yin) / 2 + 5, name, 14, "#fff", weight=700)
        end_top = (1 if odd_outer else 2, 35 if odd_outer else 36)
        end_bot = (2 if odd_outer else 1, 36 if odd_outer else 35)
        above = yout < by + bh / 2
        for k, (a, b) in ((1, (end_top[0], end_bot[0])), (18, (end_top[1], end_bot[1]))):
            x = x0 - (k - 1) * pitch
            if above:
                s.text(x, yout - 14, str(a), 10, "#e8e8e8", "middle"); s.text(x, yin + 24, str(b), 10, "#e8e8e8", "middle")
            else:
                s.text(x, yin - 14, str(b), 10, "#e8e8e8", "middle"); s.text(x, yout + 24, str(a), 10, "#e8e8e8", "middle")
    strip("P2", by + 36, by + 36 + 24, False, {})
    strip("P1", by + bh - 36, by + bh - 36 - 24, True, HOT)
    # 5V warning
    x1, y1 = x0, by + bh - 36
    s.add(f'<circle cx="{x1}" cy="{y1}" r="15" fill="none" stroke="{RED}" stroke-width="2.5"/>')
    s.text(x1 + 40, y1 + 52, "P1.1 is 5 V. Nothing ever goes in here.", 12, RED, "end", 700)
    s.text(bx + bw / 2, by - 14, "P1 has 36 sockets in 18 columns. Column 1 is at the USB-C end. Pins 1, 3, 5 ... are the outer row; 2, 4, 6 ... the inner row.", 12, MUTE, "middle")

    # zoomed strip of P1 with every socket numbered
    zx, zy, zp = 100, 560, 56
    s.text(zx, zy - 22, "P1 close up, columns 1 to 18 from the USB-C end. Every socket numbered.", 13, INK, weight=700)
    s.add(f'<rect x="{zx-16}" y="{zy-10}" width="{18*zp+32}" height="88" rx="10" fill="{BOARD}"/>')
    for k in range(1, 19):
        x = zx + (18 - k) * zp + zp / 2   # column 1 on the right, matching the board above
        for pin, y in ((2 * k, zy + 16), (2 * k - 1, zy + 56)):
            c = HOT.get(pin)
            s.add(f'<rect x="{x-14}" y="{y-14}" width="28" height="28" rx="3" fill="{c or SOCKET}" stroke="{"#fff" if c else "#4a5a5a"}" stroke-width="{2 if c else 1}"/>')
            s.text(x, y + 5, str(pin), 12, ("#fff" if c != YEL else INK) if c else "#9fb0b0", "middle", 700 if c else 400)
        s.text(x, zy + 94, f"col {k}", 9, MUTE, "middle")
    s.text(zx + 18 * zp + 24, zy + 20, "inner", 10, MUTE); s.text(zx + 18 * zp + 24, zy + 60, "outer", 10, MUTE)
    s.text(zx + 18 * zp + 24, zy + 94, "USB-C end", 9, MUTE)
    legend(s, 100, 700, [(RED, "P1.14  VDD_3V3, 3.3 V out.  Column 7, inner row"), (BLK, "P1.15  GND.  Column 8, outer row")])
    legend(s, 620, 700, [(BLU, "P1.26  I2C2_SDA, data.  Column 13, inner row"), (YEL, "P1.28  I2C2_SCL, clock.  Column 14, inner row")])
    s.save("board-pins.svg")


# --------------------------------------------------------------------------
# 3. bench-step1..4.svg: the physical build, one wire group per step
# --------------------------------------------------------------------------
def draw_bench(step):
    W, H = 1240, 880
    titles = {1: "Step 1 of 4: seat the modules", 2: "Step 2 of 4: power to each module", 3: "Step 3 of 4: the two shared columns", 4: "Step 4 of 4: four wires from the board"}
    subs = {1: "USB cable still in the bag. Push each module into the top half so every pin has its own column. The body overhangs the top edge.",
            2: "Red from each VCC/VIN column to the + rail. Black from each GND column to the - rail. Check the letters on the module before each wire.",
            3: "Pick two empty columns. Blue from every SDA to column 17. Yellow from every SCL to column 19. Nothing plugs into 17 or 19 directly.",
            4: "Turn the board so P1 faces the breadboard. Red P1.14 to +, black P1.15 to -, blue P1.26 to column 17, yellow P1.28 to column 19."}
    s = SVG(W, H, titles[step])
    s.text(32, 64, subs[step], 13, MUTE)
    bbx, bby, cols, pitch = 140, 190, 30, 30
    bbw, bbh = cols * pitch + 40, 300
    s.add(f'<rect x="{bbx}" y="{bby}" width="{bbw}" height="{bbh}" rx="10" fill="{BB}" stroke="{BB_EDGE}" stroke-width="2"/>')
    def cx(c): return bbx + 20 + (c - 1) * pitch + 15
    def hole(x, y): s.add(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" rx="1.5" fill="#3a3a3a"/>')
    railp, railm = bby + 26, bby + 48
    s.add(f'<line x1="{bbx+22}" y1="{railp-12}" x2="{bbx+bbw-22}" y2="{railp-12}" stroke="{RED}" stroke-width="2.5"/>')
    s.add(f'<line x1="{bbx+22}" y1="{railm+12}" x2="{bbx+bbw-22}" y2="{railm+12}" stroke="{BLU}" stroke-width="2.5"/>')
    s.text(bbx + 9, railp + 5, "+", 14, RED, weight=700); s.text(bbx + 9, railm + 5, "−", 14, BLU, weight=700)
    rows_top = [bby + 86 + i * 24 for i in range(5)]
    rows_bot = [rows_top[-1] + 34 + i * 24 for i in range(5)]
    for c in range(1, cols + 1):
        hole(cx(c), railp); hole(cx(c), railm)
        for y in rows_top + rows_bot: hole(cx(c), y)
        if c % 5 == 0 or c == 1: s.text(cx(c), rows_bot[-1] + 18, str(c), 9, MUTE, "middle")
    for lab, y in zip("jihgf", rows_top): s.text(bbx + 8, y + 3, lab, 9, MUTE)
    for lab, y in zip("edcba", rows_bot): s.text(bbx + 8, y + 3, lab, 9, MUTE)
    mid = (rows_top[-1] + rows_bot[0]) / 2
    s.add(f'<line x1="{bbx+12}" y1="{mid}" x2="{bbx+bbw-12}" y2="{mid}" stroke="#ddd6c2" stroke-width="7"/>')
    # how a breadboard is joined, shown once
    if step == 1:
        c = 16
        s.add(f'<rect x="{cx(c)-10}" y="{rows_bot[0]-10}" width="20" height="{rows_bot[-1]-rows_bot[0]+20}" rx="3" fill="none" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="5 3"/>')
        s.add(f'<rect x="{cx(c)+10}" y="{rows_bot[0]+2}" width="500" height="66" rx="6" fill="#fff" stroke="#2a9d8f" opacity="0.95"/>')
        s.text(cx(c) + 16, rows_bot[1] + 4, "these five holes are joined inside the board: one column is one wire.", 11, "#2a9d8f")
        s.text(cx(c) + 16, rows_bot[2] + 4, "the + and − rails are joined end to end. the groove keeps top and bottom apart.", 11, "#2a9d8f")
        s.text(cx(c) + 16, rows_bot[3] + 4, "nothing is used below the groove in this build.", 11, "#2a9d8f")
    SDA_C, SCL_C = 17, 19
    if step >= 3:
        for c, col, lab in ((SDA_C, BLU, "SDA column"), (SCL_C, YEL, "SCL column")):
            s.add(f'<rect x="{cx(c)-10}" y="{rows_top[0]-10}" width="20" height="{rows_top[-1]-rows_top[0]+20}" rx="3" fill="{col}" opacity="0.12"/>')
            s.text(cx(c), rows_top[0] - 16, lab, 9, col, "middle", 700)
    # modules
    def module(c0, pins, title, kind, optional=False):
        x = cx(c0) - 15; w = len(pins) * pitch; body_h = 70; y = rows_top[0] - 12 - body_h
        fill = {"sensor": "#5a3fa0", "oled": "#2a2a44", "rtc": "#3c5a7a"}[kind]
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{body_h}" rx="5" fill="{fill}" stroke="#111" stroke-dasharray="{"6 4" if optional else "none"}"/>')
        if kind == "oled":
            s.add(f'<rect x="{x+8}" y="{y+6}" width="{w-16}" height="34" rx="2" fill="#0b0b12" stroke="#555"/>')
            s.text(x + w / 2, y + 28, "NOW  21.4 C", 9, "#8fd3ff", "middle", style='font-family="monospace"')
        elif kind == "rtc":
            s.add(f'<circle cx="{x+w-26}" cy="{y+26}" r="16" fill="#d9d9d9" stroke="#888"/>'); s.text(x + w - 26, y + 30, "CR", 8, "#555", "middle")
            s.text(x + 10, y + 26, "DS3231", 10, "#fff", weight=700)
        else:
            s.add(f'<rect x="{x+w/2-8}" y="{y+14}" width="16" height="14" rx="2" fill="#b8b8c8"/>')
            s.text(x + w / 2, y + 44, "BME280", 10, "#fff", "middle", 700)
        s.text(x + w / 2, y - 8, title, 11, INK, "middle", 700)
        for i, (lab, c) in enumerate(pins):
            px = cx(c0 + i)
            s.add(f'<line x1="{px}" y1="{y+body_h}" x2="{px}" y2="{rows_top[0]}" stroke="#9a9a9a" stroke-width="3"/>')
            s.text(px, y + body_h - 5, lab, 8, "#fff", "middle")
    module(2, [("VIN", RED), ("GND", BLK), ("SCL", YEL), ("SDA", BLU)], "sensor", "sensor")
    module(9, [("GND", BLK), ("VCC", RED), ("SCL", YEL), ("SDA", BLU)], "screen (check your pin order)", "oled")
    module(24, [("32K", None), ("SQW", None), ("SCL", YEL), ("SDA", BLU), ("VCC", RED), ("GND", BLK)], "clock (optional, later)", "rtc", optional=True)
    plan = ((2, ["+", "-", "SCL", "SDA"]), (9, ["-", "+", "SCL", "SDA"]), (24, [None, None, "SCL", "SDA", "+", "-"]))
    if step >= 2:
        beside = {2: (6, 7), 9: (13, 14), 24: (30, 23)}   # free rail columns next to each module
        for c0, order in plan:
            pc, mc = beside[c0]
            for i, t in enumerate(order):
                col = c0 + i
                if t == "+": s.wire([(cx(col), rows_top[1]), (cx(col), rows_top[1] + 10), (cx(pc), rows_top[1] + 10), (cx(pc), railp)], RED)
                elif t == "-": s.wire([(cx(col), rows_top[2]), (cx(col), rows_top[2] + 10), (cx(mc), rows_top[2] + 10), (cx(mc), railm)], BLK)
        if step == 2:
            s.text(bbx, bby - 90, "The module body sits over the rails, so each power wire runs from the module's column (row i or h) to the nearest free rail hole beside it.", 12, INK)
            s.text(bbx, bby - 72, "The rail is one wire end to end, so which hole does not matter. Red always ends on +, black always on −.", 12, INK)
    if step >= 3:
        for c0, order in plan:
            for i, t in enumerate(order):
                col = c0 + i
                if t == "SCL": s.wire([(cx(col), rows_top[3]), (cx(col), rows_top[3] + 12), (cx(SCL_C), rows_top[3] + 12), (cx(SCL_C), rows_top[3])], YEL)
                elif t == "SDA": s.wire([(cx(col), rows_top[4]), (cx(col), rows_top[4] + 12), (cx(SDA_C), rows_top[4] + 12), (cx(SDA_C), rows_top[4])], BLU)
    # board, rotated so P1 faces the breadboard: USB-C left, pin 1 at left
    bx, by, bw, bh = 250, 590, 760, 250
    s.add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="60" fill="{BOARD}" stroke="{BOARD_EDGE}" stroke-width="2"/>')
    s.add(f'<rect x="{bx-14}" y="{by+bh/2-24}" width="28" height="48" rx="7" fill="#c8c8c8" stroke="#777"/>')
    s.text(bx - 22, by + bh / 2 + 4, "USB-C (leave unplugged)", 11, INK, "end")
    s.add(f'<rect x="{bx+110}" y="{by+bh/2-30}" width="100" height="64" rx="5" fill="#a7b3b3"/>'); s.text(bx + 160, by + bh / 2 + 6, "microSD", 10, "#123", "middle")
    s.text(bx + bw - 30, by + bh / 2 + 6, "board turned 180°: P1 is now the top strip, pin 1 at the left", 11, "#c9d3d3", "end", style='font-style="italic"')
    hp, hx0 = 38, bx + 50
    yout, yin = by + 26, by + 48
    for k in range(1, 19):
        x = hx0 + (k - 1) * hp; odd, even = 2 * k - 1, 2 * k
        for pin, y in ((odd, yout), (even, yin)):
            c = HOT.get(pin) if step == 4 else None
            s.add(f'<rect x="{x-7}" y="{y-7}" width="14" height="14" rx="2" fill="{c or SOCKET}" stroke="{"#fff" if c else "#4a5a5a"}"/>')
            if c: s.text(x, yin + 24, f"P1.{pin}", 9, "#fff", "middle", 700)
    s.text(hx0 - 26, (yout + yin) / 2 + 4, "P1", 12, "#fff", weight=700)
    s.text(hx0, yout - 12, "1", 9, "#ddd", "middle"); s.text(hx0 + 17 * hp, yout - 12, "35", 9, "#ddd", "middle")
    s.text(hx0 - 14, yin + 14, "2", 9, "#ddd", "middle"); s.text(hx0 + 17 * hp, yin + 24, "36", 9, "#ddd", "middle")
    for k in range(1, 19):
        x = hx0 + (k - 1) * hp
        for y in (by + bh - 26, by + bh - 48): s.add(f'<rect x="{x-7}" y="{y-7}" width="14" height="14" rx="2" fill="{SOCKET}" stroke="#4a5a5a"/>')
    s.text(hx0 - 26, by + bh - 33, "P2", 12, "#fff", weight=700)
    if step == 4:
        def pinxy(pin):
            k = (pin + 1) // 2; return hx0 + (k - 1) * hp, (yout if pin % 2 else yin)
        # long wires fly over the breadboard; keep their vertical runs between
        # columns so nobody reads them as plugged into the bottom half
        right = bbx + bbw + 22
        for pin, c, ry in ((14, RED, railp), (15, BLK, railm)):
            x, y = pinxy(pin); col = 28 if pin == 14 else 27
            lane = right + (0 if pin == 14 else -12)
            s.wire([(x, y), (x, by - 34 - (0 if pin == 14 else 10)), (lane, by - 34 - (0 if pin == 14 else 10)), (lane, ry), (cx(col), ry)], c)
        for pin, c, col in ((26, BLU, SDA_C), (28, YEL, SCL_C)):
            x, y = pinxy(pin); tx = cx(col) + (-15 if pin == 26 else 15); drop = by - 60 if pin == 26 else by - 46
            s.wire([(x, y), (x, drop), (tx, drop), (tx, rows_top[4] + 14), (cx(col), rows_top[4])], c)
        s.text(32, H - 16, "Say it out loud while you check: red leaves 14 and arrives at +. Black leaves 15 and arrives at −. Blue leaves 26 and arrives at 17. Yellow leaves 28 and arrives at 19.", 12, INK)
    legend(s, 1090, 96, [(RED, "3.3 V"), (BLK, "ground")]); legend(s, 1090, 140, [(BLU, "SDA (data)"), (YEL, "SCL (clock)")])
    s.save(f"bench-step{step}.svg")
    if step == 4:
        with open(os.path.join(OUT, "bench-step4.svg")) as f: data = f.read()
        with open(os.path.join(OUT, "bench-layout.svg"), "w") as f: f.write(data)
        print("wrote bench-layout.svg")


if __name__ == "__main__":
    draw_wiring()
    draw_board()
    for i in (1, 2, 3, 4):
        draw_bench(i)
