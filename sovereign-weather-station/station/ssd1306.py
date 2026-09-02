"""Minimal SSD1306 128x64 OLED driver: framebuffer, 5x7 font, I2C.

No external font files, no imaging library. Everything the screen shows is
built from the bitmaps below, which a student can read and change.
"""
FONT = {
 ' ':0x00000000_00,'0':0x3E5149453E,'1':0x0042_7F4000,'2':0x4261514946,
 '3':0x2141454B31,'4':0x1814127F10,'5':0x2745454539,'6':0x3C4A494930,
 '7':0x0171090507,'8':0x3649494936,'9':0x0649493E00,'.':0x0000600000,
 '-':0x0808080808,':':0x0036360000,'%':0x2213086462,'/':0x2010080402,
 'A':0x7E1111117E,'B':0x7F49494936,'C':0x3E41414122,'D':0x7F4141221C,
 'E':0x7F49494941,'F':0x7F09090901,'G':0x3E4149493A,'H':0x7F0808087F,
 'I':0x00417F4100,'J':0x2040413F01,'K':0x7F08142241,'L':0x7F40404040,
 'M':0x7F0204027F,'N':0x7F0408107F,'O':0x3E4141413E,'P':0x7F09090906,
 'Q':0x3E4151215E,'R':0x7F09192946,'S':0x2649494932,'T':0x01017F0101,
 'U':0x3F4040403F,'V':0x1F2040201F,'W':0x3F4038403F,'X':0x6314081463,
 'Y':0x0304780403,'Z':0x6151494543,
}
def _glyph(ch):
    v = FONT.get(ch.upper(), 0)
    return [(v >> (8 * (4 - i))) & 0xFF for i in range(5)]


class SSD1306:
    W, H = 128, 64

    def __init__(self, bus, addr=0x3C):
        self.bus, self.addr = bus, addr
        self.buf = bytearray(self.W * self.H // 8)
        for c in (0xAE, 0x20, 0x00, 0xB0, 0xC8, 0x00, 0x10, 0x40, 0x81, 0x7F,
                  0xA1, 0xA6, 0xA8, 0x3F, 0xA4, 0xD3, 0x00, 0xD5, 0xF0, 0xD9,
                  0x22, 0xDA, 0x12, 0xDB, 0x20, 0x8D, 0x14, 0xAF):
            self.cmd(c)

    def cmd(self, c):
        self.bus.write_byte_data(self.addr, 0x00, c)

    def clear(self):
        for i in range(len(self.buf)):
            self.buf[i] = 0

    def pixel(self, x, y, on=1):
        if 0 <= x < self.W and 0 <= y < self.H:
            i = x + (y // 8) * self.W
            if on: self.buf[i] |= (1 << (y % 8))
            else:  self.buf[i] &= ~(1 << (y % 8))

    def text(self, s, x, y, scale=1):
        for ch in s:
            for col, bits in enumerate(_glyph(ch)):
                for row in range(7):
                    if bits & (1 << row):
                        for a in range(scale):
                            for b in range(scale):
                                self.pixel(x + col * scale + a, y + row * scale + b)
            x += 6 * scale
        return x

    def show(self):
        for page in range(self.H // 8):
            self.cmd(0xB0 + page); self.cmd(0x00); self.cmd(0x10)
            row = self.buf[page * self.W:(page + 1) * self.W]
            for i in range(0, self.W, 16):
                self.bus.write_i2c_block_data(self.addr, 0x40, list(row[i:i + 16]))
