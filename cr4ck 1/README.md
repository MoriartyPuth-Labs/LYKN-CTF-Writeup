# cr4ck 1 — KeygenMe (reverse, Windows PE)

**Flag:** `LYKNCTF{k3yg3n_h3ll_s3lfh4sh_4ntidbg_h1dd3n_us3r_2026}`

## First look

Run `KeygenMe.exe` and you get a plain Win32 dialog: a name field, a
serial field, and a "Check it!" button. Pull the imports and it's the
expected GUI-app set — `GetDlgItemTextA`, `MessageBoxA`, `lstrcmpA`,
`strncmp` — plus one that stands out, `NtQueryInformationProcess`, which
usually means a debugger check is somewhere in the mix.

## What the binary is actually doing

Nothing here compares against a plaintext string. Instead:

- On startup, a helper builds a 256-byte table via an **RC4 Key
  Scheduling Algorithm**, keyed with `L0i_Y3u_Kh0_N0i`. That table isn't
  used to encrypt a stream in the usual RC4 sense — the binary just reads
  fixed indices out of the resulting permutation wherever it needs
  "random"-looking bytes.
- The **required username** (`th3_LYKN_v3nd0r`) is reconstructed from
  that table: eight bytes come from one set of table indices XORed with
  a fixed mask, the remaining seven from another set of indices five
  apart. It never sits anywhere in the binary as a readable string — you
  won't find it with `strings`.
- A **license-key algorithm** feeds the username through the same RC4
  table three times, at offsets 0, 7, and 14, mixing four 32-bit
  accumulators together with rotate/xor/multiply-by-constant, then packs
  the result into a `XXXX-XXXX-XXXX-XXXX-XXXX` string with its own
  checksum group on the end.
- An **anti-debug mask** gets built from four separate checks —
  `PEB.BeingDebugged`, `PEB.NtGlobalFlag & 0x70`,
  `NtQueryInformationProcess(ProcessDebugPort)`, and
  `ProcessDebugFlags == 0` — each contributing one bit. In a clean run
  the mask comes out `0`. The interesting part is that this mask isn't
  just a "refuse to run under a debugger" gate — its value actually feeds
  into both the license algorithm and the flag's key derivation, so
  patching the debugger check out with a jump wouldn't be enough on its
  own; you'd still need the mask value a clean run actually produces.
- Finally, the **flag itself is encrypted**, not compared. The decryption
  key comes from `SHA256(username || 0x1f || license || 0x1f ||
  SHA256(.text) || anti_debug_byte)`, stretched into a keystream and
  XORed against a blob sitting in `.rdata`. Get the username or the
  license even slightly wrong and you get garbage bytes instead of a
  flag — there's no separate pass/fail check to brute-force against, the
  correctness signal *is* getting a readable string out.

## Solving it

Because the username, the license, and the flag are all derived from the
same RC4 table and the same `.text` hash, the whole thing resolves in a
straight line once you have the table:

1. Run the RC4 KSA with the hardcoded key to rebuild the 256-byte state.
2. Pull the username straight out of it.
3. Feed the username through the license algorithm.
4. Hash `.text`, derive the keystream from username + license + that
   hash, and decrypt the flag blob.

`solve.py` does exactly that and is verified end-to-end against the real
`KeygenMe.exe`:

```
$ python3 solve.py KeygenMe.exe
[+] Username : th3_LYKN_v3nd0r
[+] License  : 7211-57C4-CD96-CC26-5B67
[+] Flag     : LYKNCTF{k3yg3n_h3ll_s3lfh4sh_4ntidbg_h1dd3n_us3r_2026}
```

## Tools

- **Capstone** / manual PE header parsing — locating the RC4 KSA, the
  username-recovery indices, the license mixer, and the anti-debug checks
  in the disassembly
- Plain Python `hashlib`/`struct` for the solver — no emulator needed
  here, since every step is a closed-form transform once the RC4 table is
  known
