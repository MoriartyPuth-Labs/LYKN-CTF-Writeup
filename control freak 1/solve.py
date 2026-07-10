#!/usr/bin/env python3
"""
Control Freak 1 -- solver
Invert the 3-round (keyed-transform + permutation + chained-XOR) checker.

All constants below come straight from chall-2's .rodata.
"""
key1 = [82, 100, 113, 81, 84, 118, 45, 57]          # b"RdqQTv-9"
key2 = [23, 139, 35, 66, 193, 94, 9, 167]
perm = [3, 10, 17, 24, 31, 5, 12, 19, 26, 0, 7, 14, 21, 28, 2, 9, 16, 23, 30,
        4, 11, 18, 25, 32, 6, 13, 20, 27, 1, 8, 15, 22, 29]
target = [102, 21, 228, 52, 12, 27, 62, 211, 34, 209, 234, 37, 134, 18, 136,
          111, 174, 87, 114, 24, 201, 219, 16, 54, 62, 11, 72, 7, 68, 249, 1, 255, 7]
N = 33

def rotl(v, c): c &= 7; return ((v << c) | (v >> (8 - c))) & 0xFF
def rotr(v, c): c &= 7; return ((v >> c) | (v << (8 - c))) & 0xFF

def inner_f(b, i, r):
    A = (3 * r + i) & 7; B = (r + 5 * i) & 7; ROT = ((i + r) % 7) + 1
    edi = (0x1d * r + 0xd * i) & 0xFF
    return (key2[B] + edi + rotl((key1[A] ^ b), ROT)) & 0xFF

def inner_inv(o, i, r):
    A = (3 * r + i) & 7; B = (r + 5 * i) & 7; ROT = ((i + r) % 7) + 1
    edi = (0x1d * r + 0xd * i) & 0xFF
    x = (o - key2[B] - edi) & 0xFF
    return (rotr(x, ROT) ^ key1[A]) & 0xFF

def round_f(buf, r):
    a = [inner_f(buf[i], i, r) for i in range(N)]
    t = [0] * N
    for i in range(N):
        t[perm[i]] = a[i]
    S0 = (0x5a + 0x31 * r) & 0xFF
    out = [0] * N; prev = S0
    for i in range(N):
        prev = prev ^ (t[i] ^ ((r + 7 * i) & 0xFF)); out[i] = prev & 0xFF
    return out

def round_inv(out, r):
    S0 = (0x5a + 0x31 * r) & 0xFF
    t = [0] * N; prev = S0
    for i in range(N):
        t[i] = (out[i] ^ prev ^ ((r + 7 * i) & 0xFF)) & 0xFF; prev = out[i]
    a = [t[perm[i]] for i in range(N)]
    return [inner_inv(a[i], i, r) for i in range(N)]

# invert rounds 2, 1, 0
buf = target[:]
for r in (2, 1, 0):
    buf = round_inv(buf, r)
flag = bytes(buf)
print("recovered:", flag)

# verify forward
chk = buf[:]
for r in (0, 1, 2):
    chk = round_f(chk, r)
print("verify forward == target:", chk == target)
