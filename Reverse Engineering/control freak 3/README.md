# Control Freak 3

- **Category:** Reverse Engineering (x86-64 ELF, SIGTRAP-driven bytecode VM)
- **Difficulty:** Hard — a control-flow-flattened hash VM
- **Flag:** `LYKNCTF{0UT_0F_C0NTR0L_VM2026}`

## Challenge Scenario

> Control Again!!!

## Files

- `chall-4` — `ELF 64-bit LSB executable, x86-64` (non-PIE, base `0x400000`), stripped
- `chall-4.exe` — Windows build

## TL;DR

The checker is a **control-flow-flattened bytecode VM** dispatched through a **SIGTRAP
handler** and an 8-entry jump table. It runs 5 rounds of SplitMix64-decrypted bytecode
through 8 opcode handlers (each a different hash-mixer using xxHash/SHA/FNV constants),
folding results into an OR-accumulator `qword[rsp]`. **Success = the accumulator is 0**
after all rounds — i.e. every VM instruction hashes a small group of input bytes and must
produce 0. Anti-debug (timing loop + `/proc/self/status` TracerPid) only corrupts a key
`r15` that is **0 in a clean run**.

Because there is **no early-exit on wrong bytes** (a single final OR compare), a native
brute or timing side-channel doesn't work — but **emulation does**:

1. Build a **Unicorn** x86-64 harness that maps `chall-4`, stubs the anti-debug libc calls
   (`ptrace`→0, `clock_gettime`→fixed, `/proc` reads→EOF, pre-set the SIGTRAP flag), and
   patches the 0x50000-iteration timing loop to 1 iteration for speed (~0.01 s/run).
2. Trace every `or qword[rsp], reg` site and every read of the input buffer to learn
   **which input-byte indices each constraint touches**. This reveals a perfectly
   **triangular** structure: every position `p` has a single-byte constraint `(p,)` plus
   multi-byte groups that all "close" at `p` (their max index == `p`).
3. **Solve left-to-right**: for each position `p`, brute the byte (32..126) that makes all
   groups closing at `p` evaluate to 0. Every position has a unique solution → the flag
   falls out.

Verified in WSL: `./chall-4 'LYKNCTF{0UT_0F_C0NTR0L_VM2026}'` → `Correct!`.

## Key addresses (in `chall-4`)

| Addr | Meaning |
|------|---------|
| `0x402260` | SIGTRAP handler (sets clean flag `[0x40509c]=1`) |
| `0x401120` | `main` |
| `0x402039` | verdict: `cmp qword[rsp], 0` → `Correct!` if 0 |
| `0x401cb4 / 0x401d7f / 0x401df5 / 0x401f86 / 0x401eef` | the `or qword[rsp], reg` accumulation sites |
| `[rsp+0x160]` | decoded input buffer |
| PLT `0x401030..0x401110` | getenv, raise, __errno_location, strncpy, puts, clock_gettime, fclose, printf, strcspn, fgets, signal, strtol, ptrace, fopen, strstr |

## Why emulate instead of hand-reverse?

Statically decoding 8 xxHash/SHA/FNV opcode handlers + the SplitMix64 bytecode decode + the
SIGTRAP dispatch is error-prone. Running the *actual* validator in Unicorn is ground truth:
you don't need to understand each hash, only *which bytes each constraint reads* and
*whether it evaluates to 0*. That reduces the whole thing to a triangular constraint solve.

## Note on the emulator's accumulator

In this Unicorn harness the final accumulator carries a small `0xff` residual (an
anti-debug `r15` value that would be exactly 0 on real hardware in a clean run). That means
`emu4.run(correct_flag)` prints `Nope` / `acc=0xff` — but the **77 per-instruction group
constraints all evaluate to 0**, which is what `solve4c.py` keys on. The recovered flag is
verified on the real binary:

```
$ ./chall-4 'LYKNCTF{0UT_0F_C0NTR0L_VM2026}'
Correct!
```

## Flag

```
LYKNCTF{0UT_0F_C0NTR0L_VM2026}
```

## Tools

- **Unicorn Engine** (Python, `unicorn`) — emulate the validator, `pip install unicorn`
- **Capstone** — disassembly to find the accumulation sites / PLT map
- WSL + `qemu-user` — verify the recovered flag on the real binary

## Files in this folder

- `emu4.py` — the Unicorn harness. `run(flag_bytes, trace_or=True)` returns
  `(puts_output, accumulator, or_events)`, where `or_events` is a list of
  `(site, value, [input_byte_indices])`. Point `ELF` at your copy of `chall-4`.
- `solve4c.py` — triangular solver: learns the closing groups per position, brutes each
  byte to zero them, prints the flag.

Run: `py -3.12 solve4c.py` (needs `emu4.py` + `chall-4` alongside).
