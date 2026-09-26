#!/usr/bin/env python3
"""Run the station code against a fake I2C bus.

Catches the things that are expensive to find on a board at 2am: bad
compensation maths, a framebuffer that writes off the end, a CSV that loses a
row. Does not prove the wiring is right. Nothing here touches hardware.

    python3 test_station.py
"""
import sys, os, csv, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'station'))

FAILED = []
def check(name, cond, detail=''):
    print(('  ok   ' if cond else '  FAIL ') + name + (('  ' + detail) if detail else ''))
    if not cond: FAILED.append(name)

# ---- a fake BME280 on a fake bus -------------------------------------------
# Calibration values are a plausible real set; raw values correspond to roughly
# room temperature at sea level.
CAL_88 = [110,111, 60,103, 24,251, 145,143, 187,214, 189,11, 22,30, 255,249,
          255,140, 60,208, 208,11, 203,30]
CAL_E1 = [78,1, 0, 22,44, 3, 30]

class FakeBus:
    def __init__(self, chip_id=0x60, present=(0x76, 0x3C)):
        self.chip_id, self.present = chip_id, present
        self.writes = []
    def _guard(self, addr):
        if addr not in self.present: raise OSError('no device at 0x%02X' % addr)
    def read_byte(self, addr): self._guard(addr); return 0
    def read_byte_data(self, addr, reg):
        self._guard(addr)
        if reg == 0xD0: return self.chip_id
        if reg == 0xF3: return 0x00          # never busy
        if reg == 0xA1: return 75            # H1
        return 0
    def read_i2c_block_data(self, addr, reg, n):
        self._guard(addr)
        if reg == 0x88: return CAL_88[:n]
        if reg == 0xE1: return CAL_E1[:n]
        if reg == 0xF7: return [0x51,0xD8,0x00, 0x81,0xE0,0x00, 0x6E,0x40]
        return [0]*n
    def write_byte_data(self, addr, reg, val):
        self._guard(addr); self.writes.append((addr, reg, val))
    def write_i2c_block_data(self, addr, reg, data):
        self._guard(addr)
        if len(data) > 32: raise ValueError('i2c block too long: %d' % len(data))
        self.writes.append((addr, reg, tuple(data)))

print('\nBME280 driver')
from bme280 import BME280, CHIP_BME280, CHIP_BMP280
b = BME280(FakeBus())
check('identifies a real BME280', b.chip_id == CHIP_BME280 and b.has_humidity)
t, p, h = b.read()
check('temperature is a plausible number', -60 < t < 70, '%.2f C' % t)
check('pressure is a plausible number', 300 < p < 1200, '%.1f hPa' % p)
check('humidity is inside 0-100', h is not None and 0 <= h <= 100, '%.1f %%' % h)
check('forced-mode write happened', any(r == 0xF4 for _, r, _ in b.bus.writes))

b2 = BME280(FakeBus(chip_id=CHIP_BMP280))
t2, p2, h2 = b2.read()
check('a BMP280 is detected, not mistaken for a BME280', not b2.has_humidity)
check('a BMP280 returns no humidity rather than a wrong one', h2 is None)
try:
    BME280(FakeBus(chip_id=0x1A)); check('unknown chip raises', False)
except OSError:
    check('unknown chip raises rather than reporting nonsense', True)

print('\nSSD1306 driver')
from ssd1306 import SSD1306, FONT, _glyph
s = SSD1306(FakeBus())
check('buffer is 1024 bytes for 128x64', len(s.buf) == 1024)
s.clear(); s.pixel(0, 0); check('a pixel sets exactly one bit', sum(bin(v).count('1') for v in s.buf) == 1)
s.clear()
s.pixel(-5, 5); s.pixel(200, 5); s.pixel(5, 999)
check('off-screen pixels are ignored, not wrapped', all(v == 0 for v in s.buf))
s.clear(); s.text('MONTH CARD  NOV', 2, 0)
check('text writes something', any(v for v in s.buf))
s.clear(); s.text('12.4 C', 2, 14, 2)
check('double-size text stays in the buffer', len(s.buf) == 1024)
missing = [c for c in 'NOW SINCE MIN MAX MEAN LAST MONTH CARD RH HPA 0123456789.-:%'
           if c.upper() not in FONT]
check('every character the screen uses has a glyph', not missing, str(missing))
s.show()
blocks = [w for w in s.bus.writes if isinstance(w[2], tuple)]
check('show() sends 8 pages of 128 bytes', len(blocks) == 8*8, '%d blocks' % len(blocks))

print('\nlogging and stats')
import station as st
tmp = tempfile.mkdtemp()
st.DATA_DIR = tmp; st.CSV_PATH = os.path.join(tmp, 'readings.csv')
class FakeStation(st.Station):
    def __init__(self):
        self.bus = FakeBus(); self.bus_no = 2
        self.sensor = BME280(self.bus); self.screen = SSD1306(self.bus)
        self.pending = []; self.page = 0; self.last_flush = 0
        self.n_total, self.tmin, self.tmax, self.tsum = 0, None, None, 0.0
        self.last = None
        os.makedirs(st.DATA_DIR, exist_ok=True); self._load_totals()
S = FakeStation()
for _ in range(5): S.take_reading()
check('readings are buffered, not written', len(S.pending) == 5 and not os.path.exists(st.CSV_PATH))
S.flush()
check('flush writes the file', os.path.exists(st.CSV_PATH))
check('buffer is cleared after flush', S.pending == [])
with open(st.CSV_PATH) as f: rows = list(csv.DictReader(f))
check('every buffered reading reached the card', len(rows) == 5, '%d rows' % len(rows))
check('header names are what the form expects',
      list(rows[0].keys()) == ['utc','temp_c','pressure_hpa','humidity_pct'])
S.flush(); check('flushing an empty buffer is harmless', len(list(csv.DictReader(open(st.CSV_PATH)))) == 5)
for _ in range(3): S.take_reading()
S.flush()
S2 = FakeStation()
check('totals survive a restart', S2.n_total == 8, 'n=%d' % S2.n_total)
check('min and max reload from the card', S2.tmin is not None and S2.tmax is not None)
for _ in range(3): S.page = (S.page + 1) % 3; S.draw()
check('all three screen pages render', True)
n_before, pend_before = S.n_total, len(S.pending)
S.peek(); S.draw()
check('a live peek shows on screen but is not logged or counted',
      S.n_total == n_before and len(S.pending) == pend_before and S.last is not None)

print('\nfinding the bus')
import glob as _glob
class FakeSMBus:
    """/dev/i2c-0 has the board's own devices, /dev/i2c-2 is the header."""
    layout = {0: (0x20, 0x50), 2: (0x77, 0x3C), 3: ()}
    def __init__(self, n):
        if n not in self.layout: raise OSError('no such bus')
        self.n = n
    def read_byte_data(self, addr, reg):
        if addr not in self.layout[self.n]: raise OSError('no device')
        return 0x60
    def close(self): pass
def fake_glob(pat):
    if pat.startswith('/dev/i2c-'): return ['/dev/i2c-0', '/dev/i2c-2', '/dev/i2c-3']
    return []
st.SMBus = FakeSMBus
import glob; _orig = glob.glob; glob.glob = fake_glob
st.header_bus = lambda: 2
n, bus, addr = st.find_bus()
check('sensor found on the header bus at 0x77', n == 2 and addr == 0x77, 'i2c-%d 0x%02X' % (n, addr))
FakeSMBus.layout = {0: (0x20, 0x50), 2: (0x76,), 3: ()}
n, bus, addr = st.find_bus()
check('0x76 is found too', n == 2 and addr == 0x76)
st.header_bus = lambda: None
n, bus, addr = st.find_bus()
check('without sysfs help it still finds the sensor by looking', n == 2 and addr == 0x76)
FakeSMBus.layout = {0: (0x20, 0x50), 2: (), 3: ()}
try:
    st.find_bus(); check('no sensor anywhere exits with a message', False)
except SystemExit:
    check('no sensor anywhere exits with a message', True)
glob.glob = _orig

print('\n' + ('ALL PASS' if not FAILED else 'FAILURES: ' + ', '.join(FAILED)))
sys.exit(1 if FAILED else 0)
