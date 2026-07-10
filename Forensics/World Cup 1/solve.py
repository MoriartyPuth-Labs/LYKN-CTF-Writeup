#!/usr/bin/env python3
"""World Cup 1 solver - red-channel LSB stego.
Flag: LYKNCTF{Argentina3-2CaboVerde}
"""
import sys, struct
from PIL import Image


def dump_text_chunks(path):
    d = open(path, 'rb').read()
    p = 8
    print("total size:", len(d))
    while p + 8 <= len(d):
        ln = struct.unpack('>I', d[p:p+4])[0]
        typ = d[p+4:p+8]
        if typ in (b'tEXt', b'zTXt', b'iTXt'):
            print(typ.decode(), "->", d[p+8:p+8+ln][:120])
        p += 12 + ln
        if typ == b'IEND':
            break
    trailing = d[p:]
    if trailing:
        print("TRAILING AFTER IEND:", trailing[:200])


def extract_red_lsb(path):
    im = Image.open(path).convert("RGB")
    px = list(im.getdata())
    bits = [p[0] & 1 for p in px]          # red channel LSB
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        v = 0
        for j in range(8):
            v = (v << 1) | bits[i + j]     # MSB-first
        out.append(v)
    return bytes(out)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "worldcup1_challenge.png"
    dump_text_chunks(path)
    data = extract_red_lsb(path)
    end = data.find(b'}')
    print("FLAG:", data[:end+1].decode(errors="replace"))
