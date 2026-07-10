import pefile, struct
from unicorn import *
from unicorn.x86_const import *
PATH='Serial.exe'; pe=pefile.PE(PATH); ib=pe.OPTIONAL_HEADER.ImageBase
fd=open(PATH,'rb').read()
DLGPROC=0x140001910
STACK=0x200000000; SS=0x80000; TEB=0x300000000; PEB=0x300010000
HEAP=0x400000000; STUB=0x140f00000; RET=0x140e00000
def al(x,a=0x1000): return (x+a-1)&~(a-1)
IMP={0x14000a5f0:'GetDlgItemTextA',0x14000a628:'MessageBoxA',0x14000a420:'GetModuleHandleA',
     0x14000a4d8:'memcpy',0x14000a5a0:'strlen',0x14000a5a8:'strncmp'}
class O:
    def __init__(s):
        u=Uc(UC_ARCH_X86,UC_MODE_64); s.u=u
        u.mem_map(ib, al(pe.OPTIONAL_HEADER.SizeOfImage))
        u.mem_write(ib, fd[:pe.OPTIONAL_HEADER.SizeOfHeaders])
        for sec in pe.sections:
            r=fd[sec.PointerToRawData:sec.PointerToRawData+sec.SizeOfRawData]
            if r: u.mem_write(ib+sec.VirtualAddress, r)
        u.mem_map(STACK,SS); u.mem_map(TEB,0x2000); u.mem_map(PEB,0x2000)
        u.mem_write(TEB+0x60,struct.pack('<Q',PEB)); u.reg_write(UC_X86_REG_GS_BASE,TEB)
        u.mem_map(HEAP,0x20000); u.mem_map(STUB,0x1000); u.mem_map(RET&~0xfff,0x1000)
        s.sent={}
        for i,(iat,nm) in enumerate(IMP.items()):
            a=STUB+(i+1)*0x10; u.mem_write(iat,struct.pack('<Q',a)); s.sent[a]=nm
        s.dv={}; s.msg=[]
        for a in s.sent: u.hook_add(UC_HOOK_CODE,s._imp,begin=a,end=a)
        s.snap={}
        for va,ln in [(0x140005000,0x200),(0x140009000,0x200)]:
            s.snap[va]=bytes(u.mem_read(va,ln))
    def _ret(s,rv):
        u=s.u; sp=u.reg_read(UC_X86_REG_RSP); r=struct.unpack('<Q',u.mem_read(sp,8))[0]
        u.reg_write(UC_X86_REG_RSP,sp+8); u.reg_write(UC_X86_REG_RIP,r); u.reg_write(UC_X86_REG_RAX,rv&(2**64-1))
    def _cs(s,a,mx=64):
        if not a: return b''
        o=b''
        for i in range(mx):
            c=s.u.mem_read(a+i,1)
            if c==b'\x00': break
            o+=bytes(c)
        return o
    def _imp(s,u,a,sz,ud):
        nm=s.sent[a]; rcx=u.reg_read(UC_X86_REG_RCX); rdx=u.reg_read(UC_X86_REG_RDX)
        r8=u.reg_read(UC_X86_REG_R8); r9=u.reg_read(UC_X86_REG_R9)
        if nm=='GetDlgItemTextA':
            d=s.full[:(r9&0xffffffff)-1]; u.mem_write(r8,d+b'\x00'); s._ret(len(d))
        elif nm=='GetModuleHandleA':
            s._ret(ib if rcx==0 else (0 if b'ntdll' in s._cs(rcx).lower() else ib))
        elif nm=='strlen': s._ret(len(s._cs(rcx)))
        elif nm=='strncmp':
            a1=u.mem_read(rcx,r8); b1=u.mem_read(rdx,r8); s._ret(0 if a1==b1 else 1)
        elif nm=='memcpy': u.mem_write(rcx,bytes(u.mem_read(rdx,r8))); s._ret(rcx)
        elif nm=='MessageBoxA':
            s.msg.append((s._cs(rdx),s._cs(r8))); s._ret(1)
        else: s._ret(1)
    def run(s, serial24, extra_hooks=None):
        u=s.u; s.full=b'LYKNCTF{'+serial24+b'}'; s.msg=[]
        for va,d in s.snap.items(): u.mem_write(va,d)
        # reset writable-ish (.data,.bss) each run
        rsp=STACK+SS-0x4000; sp=rsp-8; u.mem_write(sp,struct.pack('<Q',RET)); u.reg_write(UC_X86_REG_RSP,sp)
        u.reg_write(UC_X86_REG_RCX,0x1234)      # hDlg
        u.reg_write(UC_X86_REG_RDX,0x111)       # WM_COMMAND
        u.reg_write(UC_X86_REG_R8,0x3ea)        # button id
        u.reg_write(UC_X86_REG_R9,0)
        try: u.emu_start(DLGPROC, RET, timeout=15*1000000)
        except UcError as e: s.msg.append((b'ERR:'+str(e).encode(),b''))
        return s.msg
_o=None
def check(serial24):
    global _o
    if _o is None: _o=O()
    return _o.run(serial24)
if __name__=='__main__':
    m=check(b'A'*24)
    print('messages:', m)
