#!/usr/bin/env python3
"""
Control Freak 3 -- triangular solver.

The validator folds many per-instruction hashes into an OR accumulator that must be 0.
Each hash reads a small group of input-byte indices. The group structure is triangular:
every position p has a single-byte constraint (p,) plus multi-byte groups whose MAX index
is p ("closing" at p). So we solve left-to-right: for each p, brute the byte that makes
every group closing at p evaluate to 0.

Needs emu4.py and chall-4 in the same directory.
Run:  py -3.12 solve4c.py
"""
import emu4, time

L = 30   # flag length

def groups_vals(b):
    o, acc, ev = emu4.run(bytes(b), trace_or=True)
    gs = [(tuple(idxs), val) for (site, val, idxs) in ev if idxs]
    return gs, acc, o

# canonical group structure (indices are fixed by the bytecode, independent of byte values)
gs0, _, _ = groups_vals(bytes(range(0x41, 0x41 + L)))
groups = [g for g, v in gs0]
closing = {p: [gi for gi, g in enumerate(groups) if max(g) == p and max(g) < L] for p in range(L)}

cur = bytearray(b"?" * L)
t0 = time.time()
for p in range(L):
    cands = []
    for c in range(32, 127):
        cur[p] = c
        gs, acc, o = groups_vals(cur)
        if all(gs[gi][1] == 0 for gi in closing[p]):
            cands.append(c)
    if not cands:
        print("NO candidate at", p, "closing", [groups[gi] for gi in closing[p]])
        break
    cur[p] = cands[0]
    print("p=%2d cands=%s -> %r  cur=%r  t=%.0fs"
          % (p, [chr(c) for c in cands], chr(cands[0]), bytes(cur[:p + 1]), time.time() - t0),
          flush=True)

gs, acc, o = groups_vals(cur)
print("\nFINAL", bytes(cur), "acc", hex(acc) if acc is not None else None, "puts", o)
