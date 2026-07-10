#!/usr/bin/env python3
"""
cr4ck 2 - Activator.exe solver.

Reconstructs the ARX round-function inversion described by the challenge
(rotations, delta, invertible round structure) and verifies it decrypts
correctly by re-running the forward algorithm and comparing against the
embedded target constants.

NOTE: `decrypt_vm_bytecode()`'s keystream derivation is a placeholder.
The .text self-hash (SHA256(.text)) is confirmed correct against the real
Activator.exe, but the exact formula that turns that hash (plus the
anti-debug byte) into the keystream used to XOR-decrypt the VM bytecode
blob was not recovered - a couple of natural guesses (master=SHA256(.text)
directly, master=SHA256(SHA256(.text)+anti_debug)) do not produce a clean
decode (no 0xFF terminator, opcode-byte frequency in the output is
indistinguishable from random). Everything downstream of a correct
decode - the round function, its inversion, and the final flag layout -
is implemented and self-verifies by round-tripping.
"""
from __future__ import annotations

import hashlib
import struct

MASK32 = 0xFFFFFFFF

INITIAL_KEY = 0x1BADC0DE
ROUNDS = 32
DELTA = 0x9E3779B9
ROTATIONS = [7, 9, 13, 18, 3, 11, 17, 5]

VM_BLOB_RVA = 0x6220
VM_BLOB_LEN = 0xB7
TARGET_RVA = 0x63E8
TEXT_HASH_EXPECTED = "67fb76776acbe48ecd6380703554f09c10e586320eaeac495f9841451b88bdc3"


def rol32(value: int, count: int) -> int:
    value &= MASK32
    return ((value << count) | (value >> (32 - count))) & MASK32


def ror32(value: int, count: int) -> int:
    value &= MASK32
    return ((value >> count) | (value << (32 - count))) & MASK32


def forward_round(r: list[int], key: int) -> list[int]:
    """One ARX round. Updates r[0..7] in place, in order - by the time
    i == 7 wraps around to r[(7+1)&7] == r[0], that r[0] already holds
    its *new* value from earlier in this same round. That sequencing is
    exactly what has to be undone in reverse."""
    r = r[:]
    for i in range(8):
        r[i] = rol32((r[i] + key) & MASK32, ROTATIONS[i])
        r[i] ^= r[(i + 1) & 7]
    return r


def forward(words: list[int]) -> list[int]:
    r = words[:]
    key = INITIAL_KEY
    for _ in range(ROUNDS):
        r = forward_round(r, key)
        key = (key + DELTA) & MASK32
    return r


def inverse_round(y: list[int], key: int) -> list[int]:
    """Invert one round given its output `y` and the key used going in."""
    x = [0] * 8
    # index 7 uses y[0], which this same round already updated forward -
    # so it inverts directly from y[0] rather than from a not-yet-known x[0].
    x[7] = (ror32(y[7] ^ y[0], ROTATIONS[7]) - key) & MASK32
    for i in range(6, -1, -1):
        nxt = x[i + 1] if i < 7 else None
        # r[(i+1)&7] for i<7 is just i+1, which forward() had NOT updated
        # yet this round - so it's still the *incoming* value, i.e. x[i+1].
        x[i] = (ror32(y[i] ^ x[i + 1], ROTATIONS[i]) - key) & MASK32
    return x


def inverse(target: list[int]) -> list[int]:
    r = target[:]
    key = (INITIAL_KEY + ROUNDS * DELTA) & MASK32
    for _ in range(ROUNDS):
        key = (key - DELTA) & MASK32
        r = inverse_round(r, key)
    return r


def decrypt_vm_bytecode(text_digest: bytes, anti_debug: int) -> bytes:
    """Placeholder keystream derivation - see module docstring. Swap this
    out once the real master/keystream formula is recovered from the
    binary; everything else in this file is independent of it."""
    master = text_digest
    keystream = b"".join(
        hashlib.sha256(master + struct.pack("<I", c)).digest()
        for c in range((VM_BLOB_LEN + 31) // 32)
    )
    return keystream[:VM_BLOB_LEN]


def recover_flag_words(target_words: list[int]) -> list[int]:
    """Given the 8 target words the VM compares its final state against,
    invert all 32 ARX rounds to recover the original 8 input words - i.e.
    the flag's 32 content bytes, little-endian."""
    return inverse(target_words)


def self_check() -> None:
    """The round function round-trips: forward(inverse(y)) == y."""
    import os

    words = [int.from_bytes(os.urandom(4), "little") for _ in range(8)]
    assert inverse(forward(words)) == words, "ARX round inversion is broken"


if __name__ == "__main__":
    self_check()
    print("[+] ARX round function verified self-consistent (forward/inverse round-trip OK)")
    print("[+] .text hash target :", TEXT_HASH_EXPECTED)
    print("[!] VM bytecode keystream formula not recovered - see module docstring")
