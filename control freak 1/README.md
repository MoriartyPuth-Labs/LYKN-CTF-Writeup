# Control Freak 1

- **Category:** Reverse Engineering (x86-64 ELF)
- **Difficulty:** Beginner
- **Flag:** `LYKNCTF{H0W_D1D_Y0U_C0NTR0L_TH4T}`

## Challenge Scenario

> A tiny checker that really likes being in control. Can you figure out who controls the
> bytes in the end?

## Files

- `chall-2` — `ELF 64-bit LSB pie executable, x86-64, stripped` (Debian GCC 12.2.0)
- `chall-2.exe` — Windows build (same logic)

## TL;DR

The checker reads a **33-byte** flag (from `argv[1]` or the `flag:` prompt) and runs it
through **3 rounds** of `(per-byte keyed transform → fixed permutation → chained XOR)`,
then compares the 33 bytes to a fixed target in `.rodata`. Every step is a bijection, so
just invert the three rounds from the target.

"Who controls the bytes in the end" = the permutation/transposition table that reorders
the bytes.

## The round function (recovered from the disassembly)

Constants (all from `.rodata`):

```
key1 = b"RdqQTv-9"                                # 8 bytes
key2 = [23,139,35,66,193,94,9,167]                # 8 bytes
perm = [3,10,17,24,31,5,12,19,26,0,7,14,21,28,2,9,16,23,30,4,11,18,25,32,6,13,20,27,1,8,15,22,29]   # 33 entries
target = [102,21,228,52,12,27,62,211,34,209,234,37,134,18,136,111,174,87,114,24,201,219,16,54,62,11,72,7,68,249,1,255,7]   # 33 bytes
```

For round `r` (0,1,2), index `i` (0..32), input byte `b`:

**1. Inner keyed transform**
```
A   = (3*r + i) & 7
B   = (r + 5*i) & 7
ROT = ((i + r) % 7) + 1
edi = (0x1d*r + 0xd*i) & 0xFF
out[i] = ( key2[B] + edi + rotl8(key1[A] ^ b, ROT) ) & 0xFF
```
(The addressing registers `r10/r11` are derived from the stack address, but the arithmetic
cancels — `-addr_low + addr = index` — so it stays deterministic.)

**2. Permutation (scatter)**
```
t[perm[i]] = out[i]
```

**3. Chained XOR**
```
S0 = (0x5a + 0x31*r) & 0xFF
acc = S0
for i in 0..32:
    acc = acc ^ (t[i] ^ ((r + 7*i) & 0xFF))
    buf[i] = acc          # chained (each output depends on all previous)
```

Rounds are applied `r = 0, 1, 2`; the final `buf` is compared to `target`.

## Inversion

Each round is invertible:

```
chain^-1: t[i] = buf[i] ^ buf[i-1] ^ ((r+7*i)&0xFF),  buf[-1] = S0
perm^-1 : a[i] = t[perm[i]]
inner^-1: in[i] = key1[A] ^ rotr8( (a[i] - key2[B] - edi) & 0xFF, ROT )
```

Invert rounds in reverse order (2, 1, 0) starting from `target`. `solve.py` also verifies
by re-running the forward transform.

## Flag

```
LYKNCTF{H0W_D1D_Y0U_C0NTR0L_TH4T}
```

## Tools

- Python + Capstone (x86-64 disassembly)
- Pure-Python inversion (`solve.py`)

## Files in this folder

- `solve.py` — inverts the 3 rounds and prints the flag; verifies with the forward transform.
