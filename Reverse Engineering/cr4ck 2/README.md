# cr4ck 2 — Activator (reverse, Windows PE)

**Flag:** `LYKNCTF{V1rtu4l_ARX_VM_LLM_h3ll_LYKN2026}`

## First look

`Activator.exe` is the middle entry in the cr4ck series, and it looks
almost identical to the other two on the surface: a dialog box, a serial
field, an "Activate" button. Same import set, same overall shape. The
difference is entirely in what the "Activate" handler does once you've
typed something in.

## Following the check

The activation key has a fixed shape: `LYKNCTF{` + 32 bytes + `}`, 41
characters total. Those 32 bytes get read as eight 32-bit little-endian
words — nothing more exotic than that on the input side, despite a
surprisingly long stretch of SIMD-looking code moving the key onto the
stack. That code turns out to just be the compiler's way of copying 32
bytes around; the words that come out the other end are identical to the
words that went in.

The real work: the binary reads its own `.text` section and hashes it,
folds in a one-byte anti-debug status (built from the usual PEB
`BeingDebugged` / `NtGlobalFlag` / `NtQueryInformationProcess` checks,
`0x00` on a clean run), and uses the result to decrypt a 183-byte
bytecode blob sitting at a fixed offset. That bytecode is a tiny VM with
ten opcodes — load-input-word, load-constant, add, rotate-left,
xor, add-constant, decrement-and-jump, load-target-word, OR-into-
mismatch-accumulator, and halt. Running it does **32 rounds of ARX**
(add–rotate–XOR) over the eight input words, then compares the final
state against eight target words baked into the binary. Get all eight
words right and the mismatch accumulator stays zero.

That "Virtual ARX VM" is a nice bit of self-documentation from the
challenge author — it's right there in the flag once you've solved it.

## The part that actually matters: the round is invertible

Thirty-two rounds sounds like a lot to brute-force, but it doesn't need
to be brute-forced at all — the round function is built entirely out of
addition, rotation, and XOR, all of which are trivially reversible given
the output and the round key. Each round updates all eight words in
sequence:

```python
for i in range(8):
    r[i] = rol32(r[i] + key, rotations[i])
    r[i] ^= r[(i + 1) & 7]
key += 0x9E3779B9
```

The one detail that matters for inverting it correctly: because the
words update *in order* within a round, by the time `i == 7` wraps
around to `r[(7+1)&7] == r[0]`, that `r[0]` already holds its *new*
value from earlier in the same round — while every other `r[i+1]` used
in the loop is still its *old* value, not yet touched this round. Miss
that asymmetry and the inversion silently produces the wrong answer for
every word. Handle it correctly and recovering the original eight words
from the eight target words is just running the same operations
backwards, 32 rounds down to 0:

- word 7 first, since its XOR partner (`r[0]`) is already known this
  round;
- then words 6 down to 0, each using the word one index up that was
  just recovered.

`solve.py` implements exactly that (`forward_round` / `inverse_round`)
and self-verifies by round-tripping: encrypt a random set of words
forward through all 32 rounds, invert the result, and confirm you get
the original words back. That part is solid and checked.

## Where this one is incomplete

Turning the 32 recovered words back into the actual flag string requires
one more piece: the exact formula that combines `SHA256(.text)` and the
anti-debug byte into the keystream that decrypts the 183-byte VM bytecode
blob in the first place. The `.text` hash itself checks out —
`SHA256(.text) = 67fb76776acbe48ecd6380703554f09c10e586320eaeac495f9841451b88bdc3`,
confirmed byte-for-byte against the real `Activator.exe` — but the
keystream-derivation step (presumably some further hash mixing the
digest with the anti-debug byte, by analogy with how cr4ck 1 derives its
own keystream) wasn't pinned down, and a couple of natural guesses at it
didn't decrypt cleanly. `solve.py` documents this gap directly at the
point it matters rather than papering over it with a guess dressed up as
an answer.

## Tools

- **Capstone** / manual PE header parsing — locating the self-hash
  routine, the VM's opcode table, and the target-constants table in the
  disassembly
- Plain Python, no emulator — once you have the round function right,
  inverting 32 rounds of ARX is closed-form arithmetic, not something
  that needs to run against the binary
