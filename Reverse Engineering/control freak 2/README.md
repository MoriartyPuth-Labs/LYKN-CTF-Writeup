# Control Freak 2

- **Category:** Reverse Engineering (x86-64 ELF, anti-debug + control-flow flattening)
- **Difficulty:** Medium
- **Flag:** `LYKNCTF{1S_1T_H4RD_T0_C0NTR0L}`

## Challenge Scenario

> The checker looks simple: give it a flag, get Correct or Nope. But the control flow does
> not like being watched, and every wrong move quietly changes the truth. Can you take
> back control?

## Files

- `chall-3` — `ELF 64-bit LSB pie executable, x86-64, stripped` (Ubuntu GCC 15.2.0)
- `chall-3.exe` — Windows build

## TL;DR

A control-flow-flattened checker for a **30-byte** flag. Anti-debug feeds a seed
`[rsp+4]` that is **0 when the process is not traced** and becomes garbage under a debugger
(timing loop) or when `/proc/self/status` shows a non-zero `TracerPid`. With the seed = 0
(the clean value), the check is:

1. Build a fixed 256-byte **S-box** via Fisher–Yates seeded by a **golden-ratio SplitMix64**
   PRNG (constants `0x9e3779b97f4a7c15`, `0xbf58476d1ce4e5b9`, `0x94d049bb133111eb`).
2. Per input byte `i` (0..29), chained accumulator `dil` (init `0xa5`):
   ```
   x      = rol8( (prng_byte_i ^ input[i]) + (0x5a + 0x25*i), i & 7 )
   dil    = dil ^ sbox[x]
   out[i] = dil
   ```
   where `prng_byte_i = splitmix64( 0xd1b54a32d192ed03 + golden*(i+1) ) & 0xFF`.
3. Compare the 30 `out[i]` to a 30-byte target blob:
   `blob = rodata[0x2040][0:14] + rodata[0x2050][0:16]` (the two 16-byte halves overlap by
   2 bytes when loaded, giving 30 effective bytes).

Everything is invertible, so back-solve each input byte from the target.

## Inversion

Because `out[i] = out[i-1] ^ sbox[X_i]` (with `out[-1] = 0xa5`):

```
sbox[X_i] = blob[i] ^ blob[i-1]                      # blob[-1] = 0xa5
X_i       = sbox_inv[ blob[i] ^ blob[i-1] ]
input[i]  = prng_byte_i ^ ((ror8(X_i, i&7) - (0x5a+0x25*i)) & 0xFF)
```

`solve.py` builds the S-box, inverts it, and prints the flag.

## Flag

```
LYKNCTF{1S_1T_H4RD_T0_C0NTR0L}
```

## Tools

- Python + Capstone (x86-64 disassembly to recover the S-box construction and the per-byte
  transform)
- Pure-Python inversion (`solve.py`); reads the target blob straight from `chall-3`.
- WSL (`qemu-user`) optional — to *verify* the flag by running the binary untraced.

## Files in this folder

- `solve.py` — rebuilds the S-box, inverts the transform, prints the flag. Needs `chall-3`
  in the same directory (reads the target blob at `.rodata` offsets 0x2040/0x2050).
