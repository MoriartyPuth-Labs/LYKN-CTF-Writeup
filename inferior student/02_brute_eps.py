#!/usr/bin/env python3
"""
Inferior Student: Nothing Stay -- step 2
Brute-force the anti-debug byte `eps` offline and decrypt every layer.

Key derivation (from the worker):
    key = sha256(d1 + bytes([d2 ^ eps]))[:32]
    pt  = ChaCha20(key, nonce).decrypt(ct)
    ok  = sha256(pt).digest() == expected
`eps` is a single byte; in a clean run it is 0 for every chunk.

Run with:  py -3.12 02_brute_eps.py
Reads:     table.pkl
Writes:    chunkN_pl.bin  (LZMA-decompressed Python 3.12 code objects)
"""
import pickle, hashlib, lzma
from Crypto.Cipher import ChaCha20

tbl = pickle.load(open("table.pkl", "rb"))
for i, row in enumerate(tbl):
    d1, d2, nonce, ct, exp = row
    for eps in range(256):
        key = hashlib.sha256(d1 + bytes([d2 ^ eps])).digest()[:32]
        pt = ChaCha20.new(key=key, nonce=nonce).decrypt(ct)
        if hashlib.sha256(pt).digest() == exp:
            payload = lzma.decompress(pt)
            open(f"chunk{i}_pl.bin", "wb").write(payload)
            print(f"chunk{i}: eps={eps} ctlen={len(ct)} -> {len(payload)}B code object")
            break
    else:
        print(f"chunk{i}: no eps found")

# The largest chunk (index 3, ~1.7 MB) is the real main payload -- itself another
# packer of the same shape.  Marshal-load it under Python 3.12 to continue peeling,
# or just run step 3 which drives the whole thing to the flag checker.
