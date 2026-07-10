#!/usr/bin/env python3
"""Beginner Forensics PNG solver.

Recovers a repeating-XOR flag hidden in a PNG `tEXt`/Description chunk using the
flag-format prefix (LYKNCTF{) as a known-plaintext crib.

Flag: LYKNCTF{Would_Be_Nice_If_Someone_Grow_Up_One_Day}
"""
import sys, struct, codecs


def extract_description(png_path):
    """Return the raw value of the tEXt chunk keyed 'Description'."""
    d = open(png_path, 'rb').read()
    p = 8
    while p + 8 <= len(d):
        ln = struct.unpack('>I', d[p:p+4])[0]
        typ = d[p+4:p+8]
        body = d[p+8:p+8+ln]
        if typ == b'tEXt' and body.startswith(b'Description\x00'):
            return body[len(b'Description\x00'):]
        p += 12 + ln
        if typ == b'IEND':
            break
    return None


def hamming(a, b):
    return sum(bin(x ^ y).count('1') for x, y in zip(a, b))


def guess_keylen(c, maxlen=16):
    """Kasiski / normalized-Hamming key length estimate (lower = better)."""
    best = []
    for kl in range(1, maxlen + 1):
        blocks = [c[i*kl:(i+1)*kl] for i in range(len(c)//kl)]
        if len(blocks) < 2:
            break
        d = sum(hamming(blocks[i], blocks[i+1]) for i in range(len(blocks)-1))
        best.append((d / (len(blocks)-1) / kl, kl))
    best.sort()
    return best


def solve(png_path, prefix=b"LYKNCTF{"):
    val = extract_description(png_path)
    cipher = bytes.fromhex(val.decode())

    # EXIF red herring, for the record:
    # UserComment 'Gnxvat Cubgbf Znlor Sha' -> ROT13 -> 'Taking Photos Maybe Fun'
    print("[*] cipher length:", len(cipher), "bytes")
    print("[*] keylen estimate (norm-hamming, keylen):", guess_keylen(cipher)[:3])

    key = bytes(cipher[i] ^ prefix[i] for i in range(len(prefix)))  # 8-byte key
    pt = bytes(cipher[i] ^ key[i % len(key)] for i in range(len(cipher)))
    return pt


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "challeng.png"
    print("FLAG:", solve(path).decode(errors="replace"))
