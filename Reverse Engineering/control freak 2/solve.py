#!/usr/bin/env python3
"""
Control Freak 2 -- solver
Invert the golden-ratio-SplitMix64 S-box + chained transform (30-byte flag).

Needs chall-3 next to this script (reads the 30-byte target blob from .rodata).
Anti-debug seed [rsp+4] == 0 in a clean/untraced run -> that's the value we use.
"""
M = (1 << 64) - 1
golden = 0x9e3779b97f4a7c15
C1 = 0xbf58476d1ce4e5b9
C2 = 0x94d049bb133111eb

def mix(z):
    z &= M
    z = ((z ^ (z >> 30)) * C1) & M
    z = ((z ^ (z >> 27)) * C2) & M
    z = z ^ (z >> 31)
    return z & M

# --- build the 256-byte S-box: buf[0..255]=0..255, Fisher-Yates with golden SplitMix64 ---
buf = list(range(256))
rcx = golden
i = 255
while True:
    rcx = (rcx + golden) & M
    z = mix(rcx)
    j = z % (i + 1)
    buf[i], buf[j] = buf[j], buf[i]
    if rcx == 0x3779b97f4a7c1500:   # golden*256 mod 2^64 -> loop terminates after 256 iters
        break
    i -= 1
sbox = buf
inv = [0] * 256
for idx, v in enumerate(sbox):
    inv[v] = idx

# --- 30-byte target blob: rodata[0x2040][0:14] + rodata[0x2050][0:16] ---
d = open("chall-3", "rb").read()
b0 = d[0x2040:0x2050]
b1 = d[0x2050:0x2060]
blob = list(b0[:14]) + list(b1[:16])

def ror8(v, c):
    c &= 7
    return ((v >> c) | (v << (8 - c))) & 0xFF

state = 0xd1b54a32d192ed03
flag = []
prev = 0xa5                                  # dil init == blob[-1]
for i in range(30):
    prng = mix((state + golden * (i + 1)) & M) & 0xFF
    D = blob[i] ^ prev
    X = inv[D]
    t = ror8(X, i & 7)
    k = (0x5a + 0x25 * i) & 0xFF
    v = (t - k) & 0xFF
    flag.append(v ^ prng)
    prev = blob[i]

print("flag:", bytes(flag))
