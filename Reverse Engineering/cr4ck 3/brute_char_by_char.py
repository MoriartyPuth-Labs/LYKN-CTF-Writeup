import emu_serial as E, struct
O=E.O()
def run_get(serial24):
    m=O.run(serial24)
    prog=struct.unpack('<I', O.u.mem_read(0x140005008,4))[0]
    ok=any(b'accepted' in x[0] or b'OK' in x[1] for x in m)
    return prog, ok
CH=[c for c in range(0x20,0x7f) if c!=ord('}')]
serial=bytearray(b'.'*24)
for pos in range(24):
    best=(None,-1,False)
    for ch in CH:
        serial[pos]=ch
        prog, ok = run_get(bytes(serial))
        if ok:
            best=(ch,prog,True); break
        if prog>best[1]: best=(ch,prog,False)
    serial[pos]=best[0]
    print('pos %2d -> %r  progress=%d %s'%(pos,chr(best[0]),best[1],'OK' if best[2] else ''), flush=True)
    if best[2]: break
print('SERIAL:', bytes(serial).decode(errors='replace'))
print('FLAG: LYKNCTF{%s}'%bytes(serial).decode(errors='replace'))
# final verify
p,ok=run_get(bytes(serial)); print('verify ok=',ok,'progress=',p)
