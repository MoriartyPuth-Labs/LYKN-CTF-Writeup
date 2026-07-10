#!/usr/bin/env python3
"""
Inferior Student: Nothing Stay -- step 3 (the money shot)
Drive the whole packer to completion with `eps` neutralised at the crypto boundary,
then capture the innermost checker's key/nonce/target and decrypt the flag.

How it works:
 * Wrap ChaCha20.decrypt.  For every decrypt call we look up the current (d1,d2,nonce,
   ct,expected) row in the caller frames, brute the correct `eps` (0..255) on the spot,
   and RETURN the eps=0 plaintext -- so every layer runs correctly no matter what the
   anti-debug set `eps` to.  (This never touches exec/marshal/time, so it stays
   undetected.)
 * The innermost flag checker does:
       Cipher(ChaCha20(key, nonce)).encryptor().update(processed_input) == target
   with FIXED key + nonce.  Because ChaCha20 is a stream cipher, the correct flag is
   just ChaCha20(key, nonce).decrypt(target).
 * We hook builtins.input; at the flag prompt we grab the checker frame's var_* locals
   and decrypt the target directly.

Run with:  py -3.12 03_capture_and_decrypt_flag.py path\to\challl.py
"""
import sys, builtins, hashlib
from Crypto.Cipher import ChaCha20 as CC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

# ---- 1) neutralise eps at the ChaCha boundary -------------------------------------
_new = CC.new
ROWS = {}   # ct -> (d1, d2, nonce, expected)

def index_frames():
    f = sys._getframe(2); depth = 0
    while f and depth < 30:
        for scope in (f.f_locals, f.f_globals):
            for v in list(scope.values()):
                if isinstance(v, (list, tuple)):
                    cand = [v] if (len(v) == 5 and isinstance(v[0], (bytes, bytearray))) else v
                    for row in cand:
                        try:
                            d1, d2, nonce, ct, exp = row
                            if isinstance(d1, (bytes, bytearray)) and isinstance(ct, (bytes, bytearray)) \
                               and isinstance(exp, (bytes, bytearray)):
                                ROWS[bytes(ct)] = (bytes(d1), int(d2), bytes(nonce), bytes(exp))
                        except Exception:
                            pass
        f = f.f_back; depth += 1

def newnew(*a, **k):
    c = _new(*a, **k); od = c.decrypt
    def d(data=b"", *b, **kk):
        try: index_frames()
        except Exception: pass
        info = ROWS.get(bytes(data))
        if info:
            d1, d2, nonce, exp = info
            for eps in range(256):
                key = hashlib.sha256(d1 + bytes([d2 ^ eps])).digest()[:32]
                pt = _new(key=key, nonce=nonce).decrypt(data)
                if hashlib.sha256(pt).digest() == exp:
                    return pt          # always the eps=0 plaintext
        return od(data, *b, **kk)
    c.decrypt = d
    return c
CC.new = newnew

# ---- 2) capture the checker vars at the flag prompt and decrypt --------------------
def myinput(prompt=""):
    f = sys._getframe(1)
    g = {}; g.update(f.f_globals); g.update(f.f_locals)
    vars = {k: v for k, v in g.items() if k.startswith("var_") and isinstance(v, (bytes, bytearray))}
    for k, v in vars.items():
        print("[var]", k, len(v), bytes(v)[:16].hex())
    # heuristics: 32-byte key, 16-byte nonce, the long one is the target
    key   = vars.get("var_ac20c8330b5c6c16")
    nonce = vars.get("var_68f8ea7d3b0bd13e")
    target = vars.get("var_2229d99752634209")
    if key is None or nonce is None or target is None:
        by_len = sorted(vars.items(), key=lambda kv: len(kv[1]))
        key   = key   or next(v for _, v in by_len if len(v) == 32)
        nonce = nonce or next(v for _, v in by_len if len(v) == 16)
        target = target or by_len[-1][1]
    c = Cipher(algorithms.ChaCha20(bytes(key), bytes(nonce)), mode=None)
    flag = c.decryptor().update(bytes(target))
    print("\nFLAG:", flag.decode(errors="replace"))
    raise SystemExit(0)

builtins.input = myinput

path = sys.argv[1] if len(sys.argv) > 1 else "challl.py"
src = open(path, "rb").read()
try:
    builtins.exec(compile(src, "challl.py", "exec"),
                  {"__name__": "__main__", "__file__": "challl.py"})
except SystemExit:
    pass
