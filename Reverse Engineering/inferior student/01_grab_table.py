#!/usr/bin/env python3
"""
Inferior Student: Nothing Stay -- step 1
Steal the encrypted chunk table from the packer WITHOUT tripping anti-debug.

The program integrity-checks exec/marshal/time, so those cannot be hooked.
Wrapping the crypto library (Crypto.Cipher.ChaCha20) is NOT checked and is safe.

Each ChaCha20.decrypt is called by the worker with:
    TABLE[index] = (d1: bytes, d2: int, nonce: bytes, ct: bytes, expected_sha256: bytes)
TABLE lives in the caller's globals as __68a3ce74cb6bc2b44970e0c__.

Run with:  py -3.12 01_grab_table.py path\to\challl.py
Produces:  table.pkl
"""
import sys, builtins, pickle
from Crypto.Cipher import ChaCha20 as CC

_new = CC.new
done = [False]

def newnew(*a, **k):
    c = _new(*a, **k)
    od = c.decrypt
    def d(data=b"", *b, **kk):
        if not done[0]:
            g = sys._getframe(1).f_globals
            tbl = g.get("__68a3ce74cb6bc2b44970e0c__")
            if tbl is not None:
                pickle.dump(tbl, open("table.pkl", "wb"))
                done[0] = True
                sys.stderr.write("[grab] table dumped: %d chunks -> table.pkl\n" % len(tbl))
        return od(data, *b, **kk)
    c.decrypt = d
    return c

CC.new = newnew

path = sys.argv[1] if len(sys.argv) > 1 else "challl.py"
src = open(path, "rb").read()
try:
    builtins.exec(compile(src, "challl.py", "exec"),
                  {"__name__": "__main__", "__file__": "challl.py"})
except SystemExit:
    pass
except BaseException as e:
    sys.stderr.write("(program ended: %r)\n" % e)
