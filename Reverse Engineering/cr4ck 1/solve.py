#!/usr/bin/env python3
"""
cr4ck 1 solver — rebuilds the RC4 permutation table the binary generates
at startup, pulls the hidden username and license out of it, then uses
both plus a SHA-256 of .text to derive the keystream that decrypts the
embedded flag blob.
"""
import hashlib
import struct
import sys
from pathlib import Path

import pefile

MASK32 = 0xFFFFFFFF
KSA_KEY = b"L0i_Y3u_Kh0_N0i"
USERNAME_XOR_MASK = bytes.fromhex("add993f24ca678dc1d369f61e40236")
FLAG_BLOB_RVA = 0x6280
FLAG_BLOB_LEN = 0x60
FLAG_CHECK_TAG = bytes.fromhex("7db51c69a8dd7926")


def rol32(x: int, n: int) -> int:
    x &= MASK32
    return ((x << n) & MASK32) | (x >> (32 - n))


class RC4Table:
    """Just the Key Scheduling Algorithm's output permutation — the binary
    never runs the RC4 stream cipher proper, it only ever reads fixed
    indices out of this table wherever it wants a "random" byte."""

    def __init__(self, key: bytes):
        perm = list(range(256))
        j = 0
        for i in range(256):
            j = (j + perm[i] + key[i % len(key)]) & 0xFF
            perm[i], perm[j] = perm[j], perm[i]
        self.perm = perm

    def __getitem__(self, i: int) -> int:
        return self.perm[i & 0xFF]


def recover_username(table: RC4Table) -> bytes:
    high_indices = (0x42, 0x3D, 0x38, 0x33, 0x2E, 0x29, 0x24, 0x1F)
    packed = 0
    for idx in high_indices:
        packed = (packed << 8) | table[idx]
    packed ^= int.from_bytes(USERNAME_XOR_MASK[:8], "little")

    tail = bytes(
        USERNAME_XOR_MASK[8 + k] ^ table[0x47 + 5 * k] for k in range(7)
    )
    return packed.to_bytes(8, "little") + tail


def generate_license(username: bytes, table: RC4Table, anti_debug: int = 0) -> str:
    a = ((anti_debug & 0xFF) * 0x01010101) ^ 0x4C594B4E
    b = 0xAE054FB9
    c = 0x43544632
    d = 0xA5A5F00D

    for offset in (0, 7, 14):
        for ch in username:
            v = table[ch + offset]

            new_a = (rol32(a ^ v, 5) + c) & MASK32
            new_c = rol32((v + c) & MASK32, 11) ^ b
            new_b = (rol32(((v * 0x9E3779B1) & MASK32) ^ b, 17) + d) & MASK32
            a, b, c = new_a, new_b, new_c
            d = rol32((table[a] + d) & MASK32, 3) ^ a

    for _ in range(4):
        a = (a + d) & MASK32
        c ^= rol32(a, 7)
        b = (b + c) & MASK32
        d ^= rol32(b, 13)

    parts = [(a >> 16) & 0xFFFF, (a ^ c) & 0xFFFF, (c >> 16) & 0xFFFF, (b ^ d) & 0xFFFF]
    parts.append((sum(parts) ^ (b >> 16)) & 0xFFFF)
    return "-".join(f"{p:04X}" for p in parts)


def read_text_section(pe: pefile.PE) -> bytes:
    """The loader only maps VirtualSize bytes of a section, zero-filling
    the rest of that final page - so the in-memory (and self-hashed)
    image of .text is `min(raw, virtual)` real bytes padded up to
    VirtualSize, not padded up to whichever of the two is bigger."""
    for section in pe.sections:
        if section.Name.rstrip(b"\x00") == b".text":
            virtual_size = section.Misc_VirtualSize
            raw = section.get_data()[: min(section.SizeOfRawData, virtual_size)]
            return raw.ljust(virtual_size, b"\x00")
    raise ValueError(".text section not found")


def rva_to_file_offset(pe: pefile.PE, rva: int) -> int:
    return pe.get_offset_from_rva(rva)


def decrypt_flag(pe: pefile.PE, username: bytes, license_key: str, anti_debug: int = 0) -> bytes:
    text_digest = hashlib.sha256(read_text_section(pe)).digest()

    seed = hashlib.sha256(
        username + b"\x1f" + license_key.encode() + b"\x1f" + text_digest + bytes([anti_debug & 0xFF])
    ).digest()
    keystream = b"".join(hashlib.sha256(seed + struct.pack("<I", n)).digest() for n in range(3))

    off = rva_to_file_offset(pe, FLAG_BLOB_RVA)
    blob = pe.__data__[off : off + FLAG_BLOB_LEN]
    plaintext = bytes(a ^ b for a, b in zip(blob, keystream))
    flag = plaintext.split(b"\x00", 1)[0]

    tag = hashlib.sha256(b"LYKN2026" + flag).digest()
    if tag[:8] != FLAG_CHECK_TAG:
        raise ValueError("flag checksum mismatch - wrong username/license?")
    return flag


def main() -> int:
    exe_path = Path(sys.argv[1] if len(sys.argv) > 1 else "KeygenMe.exe")
    pe = pefile.PE(str(exe_path))

    table = RC4Table(KSA_KEY)
    username = recover_username(table)
    license_key = generate_license(username, table)
    flag = decrypt_flag(pe, username, license_key)

    print(f"[+] Username : {username.decode()}")
    print(f"[+] License  : {license_key}")
    print(f"[+] Flag     : {flag.decode()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
