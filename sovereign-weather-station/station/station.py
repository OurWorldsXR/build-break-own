#!/usr/bin/env python3
"""Sovereign Weather Station.

Reads the air every five minutes. Keeps the readings in memory and writes them
to the card once an hour, so the card lasts. Shows three pages on the screen.
Has no network code in it at all, because there is no network.

Runs with whatever is on the wires: sensor and screen, sensor alone, or screen
alone (Kit B wires one at a time). Keeps looking for whichever is missing, and
sets the screen up again if it stops answering, so a part that arrives late or
a wire that wobbles does not need a reboot.
"""
import csv, os, signal, subprocess, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bme280 import BME280
from ssd1306 import SSD1306
from smbus2 import SMBus

READ_EVERY   = 300          # seconds between readings
FLUSH_EVERY  = 3600         # seconds between writes to the card
DATA_DIR     = "/data"
CSV_PATH     = os.path.join(DATA_DIR, "readings.csv")
PAGE_EVERY   = 5            # seconds each screen page is shown
SHOW_EVERY   = 15           # seconds between live (unlogged) screen refreshes
LOOK_EVERY   = 10           # seconds between looks for a missing sensor or screen
REINIT_EVERY = 300          # seconds between screen re-setups, noise or not
HELLO_FOR    = 20           # seconds the station's name shows after boot
ID_PATH      = os.path.join(DATA_DIR, "station-id")


HEADER_BUS_NODE = "i2c@20020000"   # main_i2c2 on the AM62: P1.26 SDA, P1.28 SCL
SENSOR_ADDRS    = (0x76, 0x77)


def header_bus():
    """Which /dev/i2c-N is the one wired to the P1 header?

    The kernel numbers buses from the device tree aliases, so on the official
    PocketBeagle 2 image main_i2c2 is /dev/i2c-2. That is a fact about one
    image, not about the board, so look it up in sysfs rather than trusting it.
    """
    import glob, os, re
    for path in sorted(glob.glob("/sys/bus/i2c/devices/i2c-*/of_node")):
        try:
            if os.path.basename(os.readlink(path)) == HEADER_BUS_NODE:
                return int(re.search(r"i2c-(\d+)", path).group(1))
        except OSError:
            continue
    return None


def find_bus():
    """PocketBeagle 2 does not have an i2c-1. Look at what is actually there.

    Returns (bus number, open SMBus, sensor address or None). Tries the header
    bus first, then everything else, and both addresses a BME280 can sit at.
    If no sensor answers anywhere but the header bus exists, returns that bus
    with no sensor: the screen may be there alone, and the sensor may come.
    """
    import glob, re
    nums = sorted(int(re.search(r"(\d+)$", p).group(1))
                  for p in glob.glob("/dev/i2c-*"))
    h = header_bus()
    if h in nums:
        nums.remove(h); nums.insert(0, h)
    for n in nums:
        try:
            bus = SMBus(n)
        except Exception:
            continue
        for addr in SENSOR_ADDRS:
            try:
                bus.read_byte_data(addr, 0xD0)
                return n, bus, addr
            except Exception:
                pass
        try: bus.close()
        except Exception: pass
    if h in nums:
        return h, SMBus(h), None
    raise SystemExit("no header bus and no sensor on any i2c bus. run sws-check.")


def station_id():
    try:
        with open(ID_PATH) as f:
            return f.read().strip().upper() or "SWS"
    except OSError:
        return "SWS"


def usb_addresses():
    """The board's own end of the USB cable: 192.168.7.2, 192.168.6.2, or both.
    Which one a laptop reaches depends on the laptop, so show what exists."""
    try:
        out = subprocess.run(["ip", "-o", "-4", "addr"], capture_output=True,
                             text=True, timeout=5).stdout
    except Exception:
        return []
    return [w.split("/")[0] for line in out.splitlines() for w in line.split()
            if w.startswith("192.168.")][:2]


class Station:
    def __init__(self):
        self.bus_no, self.bus, addr = find_bus()
        self.sensor = self.screen = None
        if addr is not None:
            self.sensor = BME280(self.bus, addr)
        self.find_screen()
        self.pending = []
        self.page = 0
        self.last_flush = time.time()
        self.n_total, self.tmin, self.tmax, self.tsum = 0, None, None, 0.0
        self.last = None
        self.id = station_id()
        self.hello_until = time.time() + HELLO_FOR
        os.makedirs(DATA_DIR, exist_ok=True)
        self._load_totals()

    def find_sensor(self):
        for addr in SENSOR_ADDRS:
            try:
                self.sensor = BME280(self.bus, addr)
                return
            except Exception:
                pass

    def find_screen(self):
        """Setting the screen up is also how we find out if it is there."""
        try:
            self.screen = SSD1306(self.bus)
            self.last_init = time.time()
        except Exception:
            self.screen = None

    def look(self):
        """Every few seconds: find what is missing, refresh what is there."""
        if self.sensor is None:
            self.find_sensor()
        if self.screen is None:
            self.find_screen()
        elif time.time() - self.last_init >= REINIT_EVERY:
            try:
                self.screen.init(); self.last_init = time.time()
            except Exception:
                self.screen = None

    def _load_totals(self):
        if not os.path.exists(CSV_PATH):
            return
        with open(CSV_PATH) as f:
            for row in csv.DictReader(f):
                try: t = float(row["temp_c"])
                except (KeyError, ValueError): continue
                self.n_total += 1; self.tsum += t
                self.tmin = t if self.tmin is None else min(self.tmin, t)
                self.tmax = t if self.tmax is None else max(self.tmax, t)

    def take_reading(self):
        if self.sensor is None:
            return
        try:
            t, p, h = self.sensor.read()
        except Exception:
            self.sensor = None          # a wire moved. look() will find it again
            return
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.pending.append((stamp, t, p, h))
        self.last = (t, p, h)
        self.n_total += 1; self.tsum += t
        self.tmin = t if self.tmin is None else min(self.tmin, t)
        self.tmax = t if self.tmax is None else max(self.tmax, t)

    def peek(self):
        """A fresh reading for the screen only. Nothing is logged or counted."""
        if self.sensor is None:
            return
        try:
            self.last = self.sensor.read()
        except Exception:
            self.sensor = None

    def flush(self):
        """One write an hour instead of 288 a day. The card lasts 24x longer."""
        if not self.pending:
            return
        new = not os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["utc", "temp_c", "pressure_hpa", "humidity_pct"])
            for stamp, t, p, h in self.pending:
                w.writerow([stamp, round(t, 2), round(p, 2),
                            "" if h is None else round(h, 1)])
            f.flush(); os.fsync(f.fileno())
        self.pending.clear()
        self.last_flush = time.time()

    def draw(self):
        if not self.screen:
            return
        s = self.screen
        s.clear()
        if self.sensor is None or self.last is None or time.time() < self.hello_until:
            self.draw_hello()
        else:
            self.draw_page()
        try:
            s.show()
        except Exception:
            self.screen = None          # look() will set it up again

    def draw_hello(self):
        """Who this station is and where to reach it. Shown after boot, and
        whenever there is no sensor, so a station on its own can say what is
        wrong without a laptop."""
        s = self.screen
        s.text(self.id, 2, 0)
        addrs = usb_addresses() or ["192.168.7.2", "192.168.6.2"]
        s.text("SSH STUDENT AT", 2, 14)
        for i, a in enumerate(addrs):
            s.text(a, 2, 26 + 10 * i)
        if self.sensor is None:
            s.text("NO SENSOR ON WIRES" if self.page % 2 else "SCREEN OK", 2, 52)
        else:
            s.text("SENSOR OK", 2, 52)

    def draw_page(self):
        t, p, h = self.last
        s = self.screen
        if self.page == 0:
            s.text("NOW", 2, 0)
            s.text("%.1f C" % t, 2, 14, 2)
            s.text("%s%%RH  %.0f HPA" % ("--" if h is None else "%.0f" % h, p), 2, 40)
        elif self.page == 1:
            mean = self.tsum / self.n_total if self.n_total else 0
            s.text("SINCE START", 2, 0)
            s.text("MIN %5.1f  MAX %5.1f" % (self.tmin or 0, self.tmax or 0), 2, 16)
            s.text("MEAN %4.1f  N %d" % (mean, self.n_total), 2, 30)
            s.text("UNWRITTEN %d" % len(self.pending), 2, 44)
        else:
            mean = self.tsum / self.n_total if self.n_total else 0
            s.text("MONTH CARD", 2, 0)
            s.text("1 %5.1f   4 %5.0f" % (self.tmin or 0, p), 2, 16)
            s.text("2 %5.1f   5 %5s" % (self.tmax or 0,
                   "--" if h is None else "%.0f" % h), 2, 30)
            s.text("3 %5.1f   6 %5d" % (mean, self.n_total), 2, 44)


def main():
    st = Station()
    running = [True]
    def stop(*_):
        running[0] = False
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)

    st.take_reading(); st.draw()
    next_read = time.time() + READ_EVERY
    next_show = time.time() + SHOW_EVERY
    next_page = time.time() + PAGE_EVERY
    next_look = time.time() + LOOK_EVERY
    while running[0]:
        now = time.time()
        if now >= next_look:
            had_sensor = st.sensor is not None
            st.look()
            if st.sensor is not None and not had_sensor:
                st.peek()                         # arrived: show it straight away
            next_look = now + LOOK_EVERY
        if now >= next_read:
            st.take_reading(); st.draw()          # logged
            next_read = now + READ_EVERY
        elif now >= next_show:
            st.peek(); st.draw()                  # shown, not logged
            next_show = now + SHOW_EVERY
        if now >= next_page:
            st.page = (st.page + 1) % 3; st.draw()
            next_page = now + PAGE_EVERY
        if now - st.last_flush >= FLUSH_EVERY:
            st.flush()
        time.sleep(1)
    st.flush()          # never lose an hour to a clean shutdown


if __name__ == "__main__":
    main()
