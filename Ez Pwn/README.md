# Ez Pwn (pwn)

**Flag:** `LYKNCTF{If_y0u_can_s0lv3_Thi5_chall_Th3n_y0ur3_4n_4bs0lute_femb1}`

> Ez Pwn — definitely the oldest trick in the book
> `nc 15.235.202.47 8999`


## Binary

`chall` — x86-64 ELF, dynamically linked, **not stripped**.

```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

No canary + no PIE + NX means: a classic stack-smash into a ROP chain
(can't jump to shellcode, but all code addresses are fixed).

## The bug

`main()` (0x4011c5) asks for a buffer length, reads it into an `int`, then
uses it twice:

```asm
lea   rdx, [rbp-0x34]
call  scanf              ; scanf("%d", &len)
...
cmp   eax, 0x50
jle   safe                ; SIGNED comparison: len <= 80 passes
...
mov   byte ptr [rbp-5], al   ; only the LOW BYTE of len survives!
movzx edx, byte ptr [rbp-5]  ; edx (the read() size) = len & 0xFF
call  read                   ; read(0, buf, edx)
```

The bounds check is a **signed** comparison against 80, but the value
actually handed to `read()` as the byte count is `len & 0xFF` — the low
byte only. Sending `len = -1`:

- passes `cmp eax, 0x50 ; jle` (any negative number is "≤ 80" signed), and
- truncates to `0xFF` = **255** for the real `read()` size.

That gives up to 255 bytes into a buffer that's only `0xa0` (160) bytes
from the return address — a full stack smash, no canary in the way.

## Gadgets, provided for free

The binary ships a function literally named `gadget` (0x401176):

```asm
401176: push rbp
401177: mov  rbp, rsp
40117a: pop  rdi ; ret        <- POP_RDI
40117c: pop  rsi ; ret
40117e: pop  rdx ; ret
401181: pop  rbp ; ret
```

Landing one byte into `pop rdi` gives a bare `ret` (0x40117b) for free —
useful as a stack-alignment filler (see below).

## Exploit plan (ret2libc)

`system` isn't imported and NX is on, so this is a textbook two-stage
ret2libc:

1. **Leak.** ROP-call `puts(puts@got)` to leak libc's runtime address,
   then return into `main()` to reuse the exact same bug a second time.
2. **libc ID.** [libc.rip](https://libc.rip)'s symbol-fingerprint search
   (`puts`+`read`+`printf` leaked together to disambiguate) identified the
   remote as **Ubuntu 22.04 (glibc 2.35, `libc6_2.35-0ubuntu3.13`)** —
   confirmed by a page-aligned computed base.
3. **Shell.** Compute `system` and `"/bin/sh"` from the leak, ROP-call
   `system("/bin/sh")`.

### The stack-alignment gotcha

`system()` internally uses SSE instructions that fault if `rsp % 16 != 0`
at entry. Chaining only "pop reg; ret" gadgets (2 pops of 8 bytes each)
always nets a 16-byte stack shift, which **never changes the parity** —
so no combination of them fixes a misaligned call. The fix is one bare
`ret` (`PLAIN_RET = 0x40117b`, the byte right after `pop rdi`'s opcode),
which shifts `rsp` by exactly 8 bytes and flips the parity:

```
return_addr = PLAIN_RET      ; ret (8-byte alignment fix)
            = POP_RDI        ; pop rdi ; ret
            = binsh_addr     ; -> rdi
            = system_addr    ; -> call system(rdi)
```

### A synchronization gotcha

`getchar()` runs right after the length prompt to eat the trailing `\n`
left by `scanf("%d", ...)`. The **next** `puts()` after that ("Let's me
check if you are safe or not!") only prints *after* the vulnerable
`read()` call — so a client that waits for that text before sending the
payload deadlocks against a server that's already blocked waiting for
input. Send the payload immediately after the length line instead.

## Reproduction

```
python3 exploit.py REMOTE=1 HOST=15.235.202.47 PORT=8999
```

Verified live against the still-running instance:

```
[+] puts leak = 0x...   libc base = 0x74...000   (page-aligned)
$ cat flag*
LYKNCTF{If_y0u_can_s0lv3_Thi5_chall_Th3n_y0ur3_4n_4bs0lute_femb1}
```

`exploit.py` also runs unmodified against a local copy of `chall` with the
system's own libc (`python3 exploit.py`) for offline testing.

## Tools

- **pwntools** (`ELF`, `process`/`remote`, `p64`, ROP by hand)
- **libc.rip** — identifying the exact glibc build from a partial leak
- WSL/Ubuntu for a real Linux process/socket environment (binary is ELF)
