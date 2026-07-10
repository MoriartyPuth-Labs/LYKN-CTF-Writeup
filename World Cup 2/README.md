# World Cup 2

**Category:** Forensics (polyglot / appended archive)
**Status:** SOLVED
**Flag:** `LYKNCTF{RespectToCaboVerde}`

## Challenge Description

Same scenario flavor text as World Cup 1 (Messi / Cabo Verde / 5 AM Vietnam time). Provided an
image "ELIMINATED - Cape Verde are out of the World Cup" (Cape Verde goalkeeper consoling a
player). File: `worldcup2_challenge.png` (~284KB, but actually a JPEG despite the `.png` name).

## Walkthrough / Reasoning

1. **File magic check**: the file header was `ff d8 ff e0` = **JPEG**, not PNG — the `.png`
   extension was misleading.

2. **Scanned for embedded/appended data**: found the ASCII strings `flag_hidden.txt` and a `PK`
   signature near the end of the file. `PK\x03\x04` is a **ZIP local file header**.

3. This is a **polyglot / appended-ZIP**: a valid JPEG with a ZIP archive concatenated after it.
   Python's `zipfile` can open the whole file directly (ZIP readers scan from the end via the
   central directory, so trailing-archive files "just work").

4. Extracted `flag_hidden.txt` from the archive → the flag. (No password needed — plain ZIP.)

## Key Technique
Appended-archive polyglot. `zipfile.ZipFile(path)` on any file that has a ZIP structure at/near
its tail will list and extract the entries, regardless of the leading JPEG/PNG bytes.

## Tools Used
- Python 3.11 `zipfile` (stdlib)
- Manual magic-byte + `PK` signature search

## PoC / Reproduction Script
```python
import zipfile
with zipfile.ZipFile("worldcup2_challenge.png") as z:
    print(z.namelist())                       # ['flag_hidden.txt']
    print(z.read("flag_hidden.txt"))          # b'LYKNCTF{RespectToCaboVerde}'
```

Locate the signature manually (optional):
```python
d = open("worldcup2_challenge.png", "rb").read()
print(d[:4].hex())          # ffd8ffe0  -> JPEG
print(d.find(b'PK\x03\x04'))# offset of appended ZIP
```

## Reasoning Notes
- Contrast with World Cup 1 (in-pixel LSB). Here nothing is hidden in the image bitmap at all;
  the payload is simply a second file container glued on. Always check `file`/magic bytes AND
  scan for secondary container signatures (`PK`, `Rar!`, `7z`, `ustar`, second `\xff\xd8`).
