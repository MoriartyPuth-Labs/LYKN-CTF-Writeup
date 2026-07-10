# cr4ck 3 — Serial (reverse, Windows PE)

**Flag:** `LYKNCTF{Dyn4m1c_0nly_LYKN_2026!!}`

`Serial.exe` — x86-64 PE, GUI dialog app (`GetDlgItemTextA` /
`MessageBoxA` / `SendMessageA`), same family as cr4ck 1/2: a bytecode VM
gated behind a self-hash of `.text`, wrapped in a "enter your serial"
dialog. Format: `LYKNCTF{` + 24 chars + `}`.

## Why this one needed a different approach

The challenge shipped two Python "reference" scripts (`crack.py`,
`debug.py`) that reimplement the VM statically. Both are **buggy**:
tracing them showed a keystream/`edx` desync and a wrong `base` offset
per character, and — the actual root cause — both hardcode the VM's
initial seed values (`r15d = 0xc499790f`, `s78 = 0`) instead of deriving
them from the real binary.

Brute-forcing every byte at every position against these scripts' output
never produced a match, because the reachable value set for position 0
simply didn't contain the target (`EXPECTED[0] = 0x526e`) under either
hardcoded seed — confirmed with `crack.py`'s own emulator via a 256-value
sweep (see investigation below).

**The actual root cause:** both VM seeds are derived from a single global
constant, `[0x140009048] = 0xB16B00B5`, written by *startup code*
(`0x14000417a`) — code that never runs if you only emulate the check
function in isolation. Recovering that one constant and re-seeding the
emulator fixed everything immediately.

## Recovery method: Unicorn as ground truth

Rather than keep hand-debugging the static reimplementation, `emu_serial.py`
builds a **Unicorn Engine emulator of the real binary** and uses it as an
oracle:

- Maps the PE image, a stack, a fake TEB/PEB (needed since the check does
  a PEB `BeingDebugged` + `NtQueryInformationProcess` anti-debug check
  internally — irrelevant to the answer since it evaluates to "clean" in
  any properly-seeded run, but it has to not crash the emulation).
- Stubs `GetDlgItemTextA` to hand back a candidate serial, `MessageBoxA`
  to capture the verdict text, `GetModuleHandleA`/`strlen`/`strncmp`/
  `memcpy` as trivial passthroughs.
- Drives the dialog procedure directly with a synthetic `WM_COMMAND`
  (`wParam = 0x3ea`, the "Check it!" button ID) instead of pumping a real
  message loop.

```python
def check(serial24: bytes) -> list[tuple[bytes, bytes]]:
    ...  # -> [(MessageBoxA text, MessageBoxA caption), ...]
```

### Finding the per-character progress signal

The comparison loop (0x1400026f2, inside the VM-result compare) bails at
the **first mismatched character** and writes that index to a fixed
global, `[0x140005008]`. Even though the VM itself runs in constant time
per character (confirmed: instruction count is identical for every byte
tried at a fixed position — no early-bail inside the VM), the *outer
comparison* does bail early, and that global is exactly "how many leading
characters are already correct." That's the oracle signal a character-by-
character brute force needs.

### The brute force

For each of the 24 positions, try all 95 printable ASCII bytes, keep
whichever one maximizes `[0x140005008]`, lock it in, move to the next
position:

```python
for pos in range(24):
    best = (None, -1, False)
    for ch in CH:                      # 0x20..0x7e, excluding '}'
        serial[pos] = ch
        prog, ok = run_get(bytes(serial))
        if ok: best = (ch, prog, True); break
        if prog > best[1]: best = (ch, prog, False)
    serial[pos] = best[0]
```

24 positions × ~95 candidates × one Unicorn run each — a few minutes
total, fully deterministic, no guessing.

## Result

```
Dyn4m1c_0nly_LYKN_2026!!
```

→ `LYKNCTF{Dyn4m1c_0nly_LYKN_2026!!}` — final verify against the emulator
returns `ok=True, progress=24`. The serial itself is a wink at the
intended lesson: the provided *static* reference scripts were broken;
solving it required going *dynamic*.

## Files

- `emu_serial.py` — the Unicorn oracle (`O` class, `check()` entry point)
- `brute_char_by_char.py` — the 24-position brute force using the
  `[0x140005008]` progress flag
- `crack.py`, `debug.py` — the challenge-provided (buggy) static
  reimplementations, kept for reference/comparison

## Tools

- **pefile** — PE section/import parsing
- **Capstone** — x86-64 disassembly for locating the compare loop and the
  `0x140009048` startup constant
- **Unicorn Engine** — full dynamic emulation of the real check, used as
  ground truth in place of a hand-derived algorithm
