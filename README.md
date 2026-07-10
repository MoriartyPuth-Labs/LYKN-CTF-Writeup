# LYKN CTF Writeups

Writeups, solve scripts, and challenge files for solved LYKN CTF challenges.
Each folder contains a `README.md` (and often a `writeup.txt`) plus the exploit/solve scripts and
original challenge artifacts.

**35 challenges** across pwn, reverse engineering, crypto, OSINT, forensics, web, and misc.

## Pwn

| Challenge | Flag |
|---|---|
| [Ez Pwn](./Ez%20Pwn) | `LYKNCTF{If_y0u_can_s0lv3_Thi5_chall_Th3n_y0ur3_4n_4bs0lute_femb1}` |
| [ez pwn revenge](./ez%20pwn%20revenge) | `LYKNCTF{https://www.youtube.com/watch?v=Cl7FBLLi73Q...}` |
| [Glyph Cache](./Glyph%20Cache) (heap, UAF → fake vtable) | `LYKNCTF{i_hope_you_love_it_https://open.spotify.com/track/7wyBHQWBpLJAPczbzcZ8PU...}` |
| [H34p D3v1l](./H34p%20D3v1l) (heap) | `LYKNCTF{0utsm4rt3d_th3_h34p_d3v1l}` |
| [Golfing](./Golfing) (RISC-V) | `LYKNCTF{"The moon is beautiful, isn't it?"::...::#RISC!@2026%_^~}` |
| [Shop](./Shop) (logic / integer underflow) | `LYKNCTF{wr4p_wr4p_wr4p}` |
| [return to lose](./return%20to%20lose) | `LYKNCTF{97907ee12ae04a298b30bb15d1c863a6}` |

## Reverse Engineering

| Challenge | Flag |
|---|---|
| [control freak 1](./control%20freak%201) (x86-64 ELF) | `LYKNCTF{H0W_D1D_Y0U_C0NTR0L_TH4T}` |
| [control freak 2](./control%20freak%202) (anti-debug + CFF) | `LYKNCTF{1S_1T_H4RD_T0_C0NTR0L}` |
| [control freak 3](./control%20freak%203) (SIGTRAP bytecode VM) | `LYKNCTF{0UT_0F_C0NTR0L_VM2026}` |
| [cr4ck 1](./cr4ck%201) (Windows PE, KeygenMe) | `LYKNCTF{k3yg3n_h3ll_s3lfh4sh_4ntidbg_h1dd3n_us3r_2026}` |
| [cr4ck 2](./cr4ck%202) (Windows PE, Activator) | `LYKNCTF{V1rtu4l_ARX_VM_LLM_h3ll_LYKN2026}` |
| [cr4ck 3](./cr4ck%203) (Windows PE, Serial) | `LYKNCTF{Dyn4m1c_0nly_LYKN_2026!!}` |
| [i hate this app](./i%20hate%20this%20app) (Windows PE) | `LYKNCTF{setwindowdisplayaffinity}` |
| [i hate this app revenge](./i%20hate%20this%20app%20revenge) (Rust/Tauri) | `LYKNCTF{alolanvulpix}` |
| [inferior student](./inferior%20student) (Python packer + anti-debug) | `LYKNCTF{Im_At_The_PayPhone_..._F0r_2}` |
| [waguri 2](./waguri%202) (Brainfuck VM) | `LYKNCTF{K40RU_H4N4_W4_R1N_T0_S4KU}` |

## Crypto

| Challenge | Flag |
|---|---|
| [Noisy broadcast](./Noisy%20broadcast) (RSA e=3, majority voting) | recovered from `m^3` |
| [Postbox](./Postbox) (AES-CBC padding oracle) | recovered admin token |
| [Shortcut](./Shortcut) (RSA Wiener / small-d) | `LYKNCTF{95ce56e3bed44d16ba37ad2b839e984f}` |
| [twelve steps](./twelve%20steps) (LCG prediction) | `LYKNCTF{870c2a99e1aa4386b693b9fe4139a939}` |
| [whispering](./whispering) (NTRU side-channel) | `LYKNCTF{af9ccf9a4b1041a6840fa5ba9e732347}` |
| [Hash & Dash](./Hash%20%26%20Dash) (token forgery) | dynamic (live instance) |

## OSINT

| Challenge | Flag |
|---|---|
| [Far Away](./Far%20Away) (geolocation) | `LYKNCTF{ba_vi_1296m}` |
| [Miss My School](./Miss%20My%20School) | `LYKNCTF{long_bien_elementary}` |
| [Follow The Layer](./Follow%20The%20Layer) (Tron USDT tracing) | `LYKNCTF{7e401f80...8838fab:03/21/2025:FUNNULL}` |
| [Unnamed Merchant](./Unnamed%20Merchant) (MH370 / maritime) | `LYKN{HOEGH_ST_PETERSBURG_9420045_257366000_19_FILIPINO}` |
| [Important Debris](./Important%20Debris) (MH370 debris) | `LYKN{ITEM31_BAC27WPPS61_BMS4-20}` |

## Forensics

| Challenge | Flag |
|---|---|
| [Thanh Hoa 1](./Thanh%20Hoa%201) (spectrogram + AES ZIP) | `LYKNCTF{NGU01_TH4NH_H04_4N_R4U_M4_PH4_DU0NG_T4U}` |
| [World Cup 1](./World%20Cup%201) (LSB stego) | `LYKNCTF{Argentina3-2CaboVerde}` |
| [World Cup 2](./World%20Cup%202) (polyglot / appended archive) | `LYKNCTF{RespectToCaboVerde}` |
| [remedy](./remedy) (PNG appended data) | `LYKNCTF{Would_Be_Nice_If_Someone_Grow_Up_One_Day}` |

## Web

| Challenge | Flag |
|---|---|
| [waguri 1](./waguri%201) | `LYKNCTF{f3d4b9163035412cac167209455dd2b1}` |

## Misc

| Challenge | Flag |
|---|---|
| [Static](./Static) (semaphore) | `LYKN{DONTGO}` |
