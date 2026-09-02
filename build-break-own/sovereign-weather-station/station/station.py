#!/usr/bin/env python3
"""Sovereign Weather Station.

Reads the air every five minutes. Keeps the readings in memory and writes them
to the card once an hour, so the card lasts. Shows three pages on the screen.
Has no network code in it at all, because there is no network.
"""
import csv, os, signal, statistics, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bme280 import BME280, CHIP_BME280
from ssd1306 import SSD1306
from smbus2 import SMBus

READ_EVERY   = 300          # seconds between readings
FLUSH_EVERY  = 3600         # seconds between writes to the card
DATA_DIR     = "/data"
CSV_PATH     = os.path.join(DATA_DIR, "readings.csv")
STATE_PATH   = os.path.join(DATA_DIR, "station.json")
SCREEN_HOLD  = 15           # seconds the screen stays lit


def find_bus():
    """PocketBeagle 2 does not have an i2c-1. Look at what is actually there."""
    import glob, re
    for path in sorted(glob.glob("/dev/i2c-*")):
        n = int(re.search(r"(\d+)$", path).group(1))
        try:
            bus = SMBus(n)
            bus.read_byte_data(0x76, 0xD0)
            return n, bus
        except Exception:
            try: bus.close()
            except Exception: pass
    raise SystemExit("no sensor found on any i2c bus. run sws-check.")


class Station:
    def __init__(self):
        self.bus_no, self.bus = find_bus()
        self.sensor = BME280(self.bus)
        try:
            self.screen = SSD1306(self.bus)
        except Exception:
            self.screen = None
        self.pending = []
        self.page = 0
        self.last_flush = time.time()
        self.n_total, self.tmin, self.tmax, self.tsum = 0, None, None, 0.0
        self.last = None
        os.makedirs(DATA_DIR, exist_ok=True)
        self._load_totals()

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
        t, p, h = self.sensor.read()
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.pending.append((stamp, t, p, h))
        self.last = (t, p, h)
        self.n_total += 1; self.tsum += t
        self.tmin = t if self.tmin is None else min(self.tmin, t)
        self.tmax = t if self.tmax is None else max(self.tmax, t)

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
        if not self.screen or self.last is None:
            return
        t, p, h = self.last
        s = self.screen
        s.clear()
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
        s.show()


def main():
    st = Station()
    running = [True]
    def stop(*_):
        running[0] = False
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)

    st.take_reading(); st.draw()
    next_read = time.time() + READ_EVERY
    while running[0]:
        now = time.time()
        if now >= next_read:
            st.take_reading(); st.draw()
            next_read = now + READ_EVERY
        if now - st.last_flush >= FLUSH_EVERY:
            st.flush()
        time.sleep(1)
    st.flush()          # never lose an hour to a clean shutdown


if __name__ == "__main__":
    main()
