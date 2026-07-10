# I HATE THIS APP

- **Category:** Reverse Engineering (Windows PE)
- **Difficulty:** Beginner
- **Flag:** `LYKNCTF{setwindowdisplayaffinity}`

## Challenge Scenario

> Aughhh, how the hell can I not take a screenshot of this freaking app? I... I mean...
> It feels like the app is transparent to my screen. I can see it, but I can't capture it.
> Why? Am I living in a simulation or something?
>
> Your mission is to find the function that prevents me from taking screenshots.
> FLAG FORMAT: `LYKNCTF{function_name}` — all lowercase, no spaces.

## Files

- `fuoverflow_learning.rar` → `fuoverflow_learning.exe`
  - `PE32+ executable (GUI) x86-64, for MS Windows, 6 sections`

## TL;DR

The app calls the Win32 API **`SetWindowDisplayAffinity`**. With the flags
`WDA_MONITOR` / `WDA_EXCLUDEFROMCAPTURE`, the Desktop Window Manager excludes the window
from screen captures — it renders on the monitor but appears black/blank (or is skipped
entirely) in any screenshot. That is exactly the "visible but not capturable" behaviour
described. Flag = the function name, lowercased.

## Reasoning / Steps

1. Extract the RAR (WinRAR) → a stripped PE32+ GUI executable.

2. Screenshot-blocking on Windows has one canonical mechanism: the compositor-level
   **`SetWindowDisplayAffinity(hWnd, WDA_EXCLUDEFROMCAPTURE)`** (user32.dll). So the very
   first thing to check is whether that symbol is imported.

3. Confirm by scanning the binary for the import string:

   ```bash
   # from Git-Bash
   grep -a -o -i "SetWindowDisplayAffinity" fuoverflow_learning.exe | sort -u
   # -> SetWindowDisplayAffinity

   grep -a -o -i "user32" fuoverflow_learning.exe | sort | uniq -c
   # -> 7 user32   (imported from user32.dll)
   ```

   The function is present and imported from `user32.dll`. No deeper reversing needed —
   the challenge only asks for the name of the anti-screenshot function.

## Flag

```
LYKNCTF{setwindowdisplayaffinity}
```

## Tools

- WinRAR (extract)
- Git-Bash `grep` (import string search)

> Note: `strings` isn't available in this Git-Bash, so `grep -a -o` over the raw file is
> used as a drop-in.
