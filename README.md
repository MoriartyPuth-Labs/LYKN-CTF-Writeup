# LYKN CTF Writeups

Writeups, solve scripts, and challenge files for solved LYKN CTF challenges.
Each folder contains a `README.md` (and often a `writeup.txt`) plus the exploit/solve scripts and
original challenge artifacts.

**35 challenges** across pwn, reverse engineering, crypto, OSINT, forensics, web, and misc.

Difficulty is my own assessment of what the solve actually required (technique depth, tooling,
number of steps), not just the label the challenge author gave it — rated on a 5-tier scale:
**Beginner → Easy → Medium → Hard → Insane**.

## Pwn

| Challenge | Difficulty | Flag |
|---|---|---|
| [Ez Pwn](./Ez%20Pwn) | Easy | `LYKNCTF{If_y0u_can_s0lv3_Thi5_chall_Th3n_y0ur3_4n_4bs0lute_femb1}` |
| [ez pwn revenge](./ez%20pwn%20revenge) | Medium | `LYKNCTF{https://www.youtube.com/watch?v=Cl7FBLLi73Q...}` |
| [Glyph Cache](./Glyph%20Cache) (heap, UAF → fake vtable) | Hard | `LYKNCTF{i_hope_you_love_it_https://open.spotify.com/track/7wyBHQWBpLJAPczbzcZ8PU...}` |
| [H34p D3v1l](./H34p%20D3v1l) (heap) | Hard | `LYKNCTF{0utsm4rt3d_th3_h34p_d3v1l}` |
| [Golfing](./Golfing) (RISC-V) | Insane | `LYKNCTF{"The moon is beautiful, isn't it?"::...::#RISC!@2026%_^~}` |
| [Shop](./Shop) (logic / integer underflow) | Beginner | `LYKNCTF{wr4p_wr4p_wr4p}` |
| [return to lose](./return%20to%20lose) | Beginner | `LYKNCTF{97907ee12ae04a298b30bb15d1c863a6}` |

## Reverse Engineering

| Challenge | Difficulty | Flag |
|---|---|---|
| [control freak 1](./control%20freak%201) (x86-64 ELF) | Medium | `LYKNCTF{H0W_D1D_Y0U_C0NTR0L_TH4T}` |
| [control freak 2](./control%20freak%202) (anti-debug + CFF) | Medium | `LYKNCTF{1S_1T_H4RD_T0_C0NTR0L}` |
| [control freak 3](./control%20freak%203) (SIGTRAP bytecode VM) | Hard | `LYKNCTF{0UT_0F_C0NTR0L_VM2026}` |
| [cr4ck 1](./cr4ck%201) (Windows PE, KeygenMe) | Medium | `LYKNCTF{k3yg3n_h3ll_s3lfh4sh_4ntidbg_h1dd3n_us3r_2026}` |
| [cr4ck 2](./cr4ck%202) (Windows PE, Activator) | Hard | `LYKNCTF{V1rtu4l_ARX_VM_LLM_h3ll_LYKN2026}` |
| [cr4ck 3](./cr4ck%203) (Windows PE, Serial) | Hard | `LYKNCTF{Dyn4m1c_0nly_LYKN_2026!!}` |
| [i hate this app](./i%20hate%20this%20app) (Windows PE) | Beginner | `LYKNCTF{setwindowdisplayaffinity}` |
| [i hate this app revenge](./i%20hate%20this%20app%20revenge) (Rust/Tauri) | Medium | `LYKNCTF{alolanvulpix}` |
| [inferior student](./inferior%20student) (Python packer + anti-debug) | Hard | `LYKNCTF{Im_At_The_PayPhone_..._F0r_2}` |
| [waguri 2](./waguri%202) (Brainfuck VM) | Medium | `LYKNCTF{K40RU_H4N4_W4_R1N_T0_S4KU}` |

## Crypto

| Challenge | Difficulty | Flag |
|---|---|---|
| [Noisy broadcast](./Noisy%20broadcast) (RSA e=3, majority voting) | Medium | recovered from `m^3` |
| [Postbox](./Postbox) (AES-CBC padding oracle) | Medium | recovered admin token |
| [Shortcut](./Shortcut) (RSA Wiener / small-d) | Medium | `LYKNCTF{95ce56e3bed44d16ba37ad2b839e984f}` |
| [twelve steps](./twelve%20steps) (LCG prediction) | Medium | `LYKNCTF{870c2a99e1aa4386b693b9fe4139a939}` |
| [whispering](./whispering) (NTRU side-channel) | Medium | `LYKNCTF{af9ccf9a4b1041a6840fa5ba9e732347}` |
| [Hash & Dash](./Hash%20%26%20Dash) (token forgery) | Medium | dynamic (live instance) |

## OSINT

| Challenge | Difficulty | Flag |
|---|---|---|
| [Far Away](./Far%20Away) (geolocation) | Beginner | `LYKNCTF{ba_vi_1296m}` |
| [Miss My School](./Miss%20My%20School) | Beginner | `LYKNCTF{long_bien_elementary}` |
| [Follow The Layer](./Follow%20The%20Layer) (Tron USDT tracing) | Easy | `LYKNCTF{7e401f80...8838fab:03/21/2025:FUNNULL}` |
| [Unnamed Merchant](./Unnamed%20Merchant) (MH370 / maritime) | Easy | `LYKN{HOEGH_ST_PETERSBURG_9420045_257366000_19_FILIPINO}` |
| [Important Debris](./Important%20Debris) (MH370 debris) | Medium | `LYKN{ITEM31_BAC27WPPS61_BMS4-20}` |

## Forensics

| Challenge | Difficulty | Flag |
|---|---|---|
| [Thanh Hoa 1](./Thanh%20Hoa%201) (spectrogram + AES ZIP) | Medium | `LYKNCTF{NGU01_TH4NH_H04_4N_R4U_M4_PH4_DU0NG_T4U}` |
| [World Cup 1](./World%20Cup%201) (LSB stego) | Beginner | `LYKNCTF{Argentina3-2CaboVerde}` |
| [World Cup 2](./World%20Cup%202) (polyglot / appended archive) | Beginner | `LYKNCTF{RespectToCaboVerde}` |
| [remedy](./remedy) (PNG appended data) | Easy | `LYKNCTF{Would_Be_Nice_If_Someone_Grow_Up_One_Day}` |

## Web

| Challenge | Difficulty | Flag |
|---|---|---|
| [waguri 1](./waguri%201) (WebSocket race condition) | Easy | `LYKNCTF{f3d4b9163035412cac167209455dd2b1}` |

## Misc

| Challenge | Difficulty | Flag |
|---|---|---|
| [Static](./Static) (semaphore) | Beginner | `LYKN{DONTGO}` |
