#!/usr/bin/env python3
"""
Control Freak 3 -- Unicorn harness that emulates chall-4's validator.

run(flag_bytes, trace_or=False) -> (puts_output, accumulator, or_events)
  puts_output : list of bytes puts()'d (e.g. b'Correct!' / b'Nope')
  accumulator : final value of the OR accumulator qword[rsp] at the verdict (0 == Correct)
  or_events   : (only when trace_or=True) list of (site, value, sorted_input_byte_indices)
                one entry per `or qword[rsp], reg` accumulation.

Anti-debug is neutralised by:
  * stubbing the libc PLT calls (ptrace/clock_gettime/signal/raise/fopen/fgets/...),
  * pre-setting the SIGTRAP "clean" flag [0x40509c]=1,
  * patching the 0x50000-iteration timing loop (cmp rdx,0x50000 -> cmp rdx,1).

Point ELF at your copy of chall-4.
"""
import struct
from unicorn import *
from unicorn.x86_const import *

ELF = "chall-4"
data = open(ELF, "rb").read()

PLT = {
    0x401030: "getenv", 0x401040: "raise", 0x401050: "__errno_location", 0x401060: "strncpy",
    0x401070: "puts", 0x401080: "clock_gettime", 0x401090: "fclose", 0x4010a0: "printf",
    0x4010b0: "strcspn", 0x4010c0: "fgets", 0x4010d0: "signal", 0x4010e0: "strtol",
    0x4010f0: "ptrace", 0x401100: "fopen", 0x401110: "strstr",
}
# the `or qword[rsp], reg` accumulation sites and which register holds the contribution
OR_SITES = {
    0x401cb4: UC_X86_REG_RAX, 0x401d7f: UC_X86_REG_RAX, 0x401df5: UC_X86_REG_RDI,
    0x401f86: UC_X86_REG_RAX, 0x401eef: UC_X86_REG_RAX,
}

def run(flag_bytes, trace_or=False):
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    # map the four PT_LOAD segments (off, vaddr, filesz, memsz)
    for (off, va, filesz, memsz) in [(0, 0x400000, 0x8f0, 0x8f0),
                                     (0x1000, 0x401000, 0x12d1, 0x12d1),
                                     (0x3000, 0x403000, 0x734, 0x734),
                                     (0x3dd8, 0x404dd8, 0x2b0, 0x2c8)]:
        base = va & ~0xfff
        end = (va + memsz + 0xfff) & ~0xfff
        try: uc.mem_map(base, end - base)
        except Exception: pass
        uc.mem_write(va, data[off:off + filesz])

    # patch timing loop: cmp rdx, 0x50000 -> cmp rdx, 1  (imm32 at 0x4011f7)
    uc.mem_write(0x4011f7, struct.pack("<I", 1))

    STACK = 0x7fff0000; SSZE = 0x200000
    uc.mem_map(STACK, SSZE); rsp = STACK + SSZE - 0x1000
    HEAP = 0x10000; uc.mem_map(HEAP, 0x10000); hp = [HEAP + 0x100]
    def alloc(b):
        a = hp[0]; uc.mem_write(a, b); hp[0] += (len(b) + 15) & ~15; return a
    argv1 = alloc(flag_bytes + b"\x00")
    argv0 = alloc(b"./chall-4\x00")
    argv_arr = alloc(struct.pack("<QQQ", argv0, argv1, 0))
    errno_loc = alloc(b"\x00" * 8)
    fake_file = alloc(b"FILE")

    uc.mem_write(0x40509c, b"\x01\x00\x00\x00")   # SIGTRAP clean flag
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.reg_write(UC_X86_REG_RDI, 2)               # argc
    uc.reg_write(UC_X86_REG_RSI, argv_arr)        # argv

    clk = [1]; out = []; or_events = []; input_reads = []

    def readcstr(addr):
        b = b""
        while True:
            c = uc.mem_read(addr + len(b), 1)
            if c == b"\x00": break
            b += c
            if len(b) > 4096: break
        return b

    def do_plt(name):
        sp = uc.reg_read(UC_X86_REG_RSP)
        ret = struct.unpack("<Q", uc.mem_read(sp, 8))[0]
        uc.reg_write(UC_X86_REG_RSP, sp + 8)
        a0 = uc.reg_read(UC_X86_REG_RDI); a1 = uc.reg_read(UC_X86_REG_RSI); a2 = uc.reg_read(UC_X86_REG_RDX)
        rv = 0
        if name in ("getenv", "ptrace", "raise", "signal", "fclose", "printf", "fgets"):
            rv = 0
        elif name == "__errno_location":
            rv = errno_loc
        elif name == "clock_gettime":
            uc.mem_write(a1, struct.pack("<qq", 0, clk[0])); clk[0] += 5; rv = 0
        elif name == "fopen":
            rv = fake_file
        elif name == "strncpy":
            n = a2 & 0xffffffffffffffff
            b = uc.mem_read(a1, min(n, 4096)); nb = bytes(b.split(b"\x00")[0][:n])
            uc.mem_write(a0, nb + b"\x00" * (n - len(nb))); rv = a0
        elif name == "strcspn":
            s = readcstr(a0); rej = readcstr(a1); i = 0
            for ch in s:
                if ch in rej: break
                i += 1
            rv = i
        elif name == "strstr":
            hay = readcstr(a0); ned = readcstr(a1); idx = hay.find(ned)
            rv = (a0 + idx) if idx >= 0 else 0
        elif name == "strtol":
            s = readcstr(a0); j = 0
            while j < len(s) and s[j] in b" \t": j += 1
            k = j
            if k < len(s) and s[k] in b"+-": k += 1
            while k < len(s) and s[k] in b"0123456789": k += 1
            try: rv = int(s[j:k] or b"0")
            except Exception: rv = 0
            if a1: uc.mem_write(a1, struct.pack("<Q", a0 + k))
            rv &= (1 << 64) - 1
        elif name == "puts":
            out.append(readcstr(a0)); rv = 1
        uc.reg_write(UC_X86_REG_RAX, rv)
        uc.reg_write(UC_X86_REG_RIP, ret)

    def hook_plt(uc, addr, size, user):
        do_plt(PLT[addr])
    for a in PLT:
        uc.hook_add(UC_HOOK_CODE, hook_plt, begin=a, end=a)

    acc = [None]
    def hook_verdict(uc, addr, size, user):
        rspv = uc.reg_read(UC_X86_REG_RSP)
        acc[0] = struct.unpack("<Q", uc.mem_read(rspv, 8))[0]
    uc.hook_add(UC_HOOK_CODE, hook_verdict, begin=0x402039, end=0x402039)

    def hook_or(uc, addr, size, user):
        reg = OR_SITES[addr]
        val = uc.reg_read(reg) & ((1 << 64) - 1)
        or_events.append((addr, val, sorted(set(input_reads))))
        input_reads.clear()
    def hook_mem(uc, access, addr, size, value, user):
        base = uc.reg_read(UC_X86_REG_RSP) + 0x160
        if base <= addr < base + len(flag_bytes) + 1:
            input_reads.append(addr - base)
    if trace_or:
        for a in OR_SITES:
            uc.hook_add(UC_HOOK_CODE, hook_or, begin=a, end=a)
        uc.hook_add(UC_HOOK_MEM_READ, hook_mem)

    try:
        uc.emu_start(0x401120, 0x401e89, count=20000000)
    except UcError as e:
        out.append(("UCERR:" + str(e)).encode())
    return out, acc[0], or_events


if __name__ == "__main__":
    o, a, ev = run(b"LYKNCTF{" + b"a" * 21 + b"}")
    print("puts=", o, "acc=", hex(a) if a is not None else None)
