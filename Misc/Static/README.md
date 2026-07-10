# Static (misc)

**Flag:** `LYKN{DONTGO}`

> H..Hey... don't leave me yet :( Don't you find it all romantic, the way
> things used to be? Right from the moment I started making this
> challenge, I kept thinking about Semaphore. Classic, ecstatic, it's
> magic.
>
> FLAG FORMAT: LYKN{WORD}. If a word is repeated, keep only one
> occurrence of it — e.g. KITTYKITTYKITTY → LYKN{KITTY}. Uppercase only,
> strip anything that isn't a letter.
>
> HINT: This challenge is about Flag Semaphore.

## Approach

The challenge presents a **flag semaphore** encoding (the two-flag signal
alphabet, one flag position per 45°-increment octant, as used for
ship-to-ship/scout signaling — not to be confused with the CTF flag
itself). Each figure/position in the challenge material maps to one
letter via the standard semaphore alphabet:

```
A: down-left      / down          N: down-right    / left
B: down-left      / up            O: down-right    / up
C: down-left      / horizontal-l  P: down-right    / horizontal-l
D: down-left      / up-right      Q: down-right    / up-right
E: down-left      / down-right    R: down-right    / down-right (mirrored)
F: down           / up            S: left          / up
...                                (26 letters + numeral/attention signs)
```

(Full 8-direction × 8-direction alphabet table — each letter is a unique
pair of flag positions taken from the 8 compass-rose directions around the
signaler, excluding the identical-position "attention" sign.)

Decoding the sequence of positions gives a repeated word — per the
prompt's own instruction ("if a word is repeated, keep only one
occurrence"), the raw decode comes out as the target word repeated
back-to-back (e.g. `DONTGODONTGODONTGO`), collapsing to a single
occurrence: **`DONTGO`**.

Flag format `LYKN{WORD}` (this challenge's misc/OSINT set uses the
`LYKN{}` wrapper rather than `LYKNCTF{}` — noted in the master flag-format
convention for this CTF) gives:

```
LYKN{DONTGO}
```

## Tools

- Manual semaphore-alphabet lookup (two-flag-position → letter table)
- No scripting needed beyond straightforward substitution/dedup once the
  alphabet mapping is applied

## Note on reproducibility

The original challenge asset (the semaphore position diagram/image) was
not preserved from the working session, so this writeup documents the
alphabet and decode *methodology* rather than a byte-for-byte replay
against the original image. The flag above was confirmed correct in the
original session.
