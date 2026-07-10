#!/usr/bin/env python3
"""
I HATE THIS APP REVENGE  --  solver
Recovers the JPEG from the AES-256-CTR "FixedEnvelope" .enc.bin.

Cipher recovered from decrypt_fixed @ 0x1401fa2b0 in the Rust binary:
  - key   = FIXED_ENCRYPTION_KEY (default), 32 bytes -> AES-256
  - nonce = file[0:12]
  - AES-256-CTR keystream where the 16-byte counter block for block i is:
        counter_block[i] = file[0:8] ++ (7 + i).to_bytes(8, 'big')
  - plaintext = ciphertext XOR keystream  (no GCM tag)

FIXED_ENCRYPTION_KEY default is bytes[32:64] of the ASCII blob at VA 0x140c5fdf0:
    3qyJU3Z6IXlfpr2CErOHH76ugQcAoWzY  H}3t%^nDw5F?cWj-XAH!Dj8AakaD9y9M
    (FUO_PASS_SECRET, 0:32)           (FIXED_ENCRYPTION_KEY, 32:64)

Usage:
    python recover.py [chall.exe] [file.enc.bin] [out.jpg]
Defaults assume the two files sit next to this script.
"""
import sys
from Crypto.Cipher import AES

# --- Option A: hardcoded key (no exe needed) ---
FIXED_ENCRYPTION_KEY = b"H}3t%^nDw5F?cWj-XAH!Dj8AakaD9y9M"   # 32 bytes

def read_key_from_exe(exe_path):
    """Optional: pull the key straight out of the exe's .rdata (VA 0x140c5fdf0)."""
    d = open(exe_path, "rb").read()
    # .rdata: file_offset = VA - 0x140b1a000 + 0xb18e00 ; blob VA = 0x140c5fdf0
    off = 0x140c5fdf0 - (0x140000000 + 0xb1a000)  # RVA within rdata
    file_off = 0xb18e00 + off
    blob = d[file_off:file_off + 64]
    return blob[0:32], blob[32:64]   # (FUO_PASS_SECRET, FIXED_ENCRYPTION_KEY)

def decrypt(enc_path, key, out_path):
    data = open(enc_path, "rb").read()
    nonce = data[:12]
    body  = data[12:]
    ecb = AES.new(key, AES.MODE_ECB)
    nblocks = (len(body) + 15) // 16
    ks = b"".join(
        ecb.encrypt(data[0:8] + ((7 + i) & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "big"))
        for i in range(nblocks)
    )
    pt = bytes(a ^ b for a, b in zip(body, ks))
    open(out_path, "wb").write(pt)
    return pt

if __name__ == "__main__":
    exe = sys.argv[1] if len(sys.argv) > 1 else None
    enc = sys.argv[2] if len(sys.argv) > 2 else "726471288_122216388452484307_639451856029278247_n.enc.bin"
    out = sys.argv[3] if len(sys.argv) > 3 else "recovered.jpg"

    key = FIXED_ENCRYPTION_KEY
    if exe:
        fuo_pass, key = read_key_from_exe(exe)
        print("FUO_PASS_SECRET     =", fuo_pass)
        print("FIXED_ENCRYPTION_KEY=", key)

    pt = decrypt(enc, key, out)
    print("wrote", out, len(pt), "bytes")
    print("header:", pt[:16].hex(), "tail:", pt[-4:].hex())
    assert pt[:3] == b"\xff\xd8\xff", "not a JPEG - wrong key/mode?"
    print("OK: valid JPEG. Render it -> Alolan Vulpix -> LYKNCTF{alolanvulpix}")
