# Far Away

**Category:** OSINT (geolocation)
**Status:** SOLVED
**Flag:** `LYKNCTF{ba_vi_1296m}`

## Challenge Description
> "I love looking out of the window whenever I'm stuck at my university... Far away, there is a
> mountain — a really big mountain. I'm curious about the name of that mountain, and how high it
> is."

Flag format: `LYKNCTF{mountain_name + height_of_the_highest_peak_in_meters + unit}`, lowercase,
underscores between parts and between multi-word names. Example: `LYKNCTF{everest_3667m}`.

Hint: Use Google Earth 3D, project the view from the university (circled point = parking lot) and
look straight ahead. A Google Drive folder with two images was provided.

## Walkthrough / Reasoning

1. **Recover the Drive images.** WebFetch on the Drive folder listed two files but not their IDs.
   Fetched the folder HTML with `curl` and grepped for the 25–40-char Drive file IDs, then
   downloaded each via `https://drive.google.com/uc?export=download&id=<ID>`.

2. **Identify the university.** One image is the official campus map:
   **"BẢN ĐỒ TRƯỜNG ĐẠI HỌC FPT CƠ SỞ HÀ NỘI"** — FPT University, Hòa Lạc Hi-Tech Park,
   Km29 Đại lộ Thăng Long, **Thạch Thất, Hà Nội**.

3. **Line of sight.** From FPT Hòa Lạc campus the prominent big mountain to the west/northwest is
   **Núi Ba Vì (Ba Vì massif)**, famous for its distinctive **three peaks**.

4. **Height of the highest peak.** Ba Vì's three peaks are Đỉnh Vua (1,296 m), Đỉnh Tản Viên
   (1,227 m), Đỉnh Ngọc Hoa (1,131 m). Highest = **Đỉnh Vua = 1,296 m** (also the highest point
   in Hanoi; has a Ho Chi Minh shrine on the summit).

## Answer Construction
mountain name "Ba Vi" → `ba_vi`; height 1296 m → `1296m`  ⇒ `LYKNCTF{ba_vi_1296m}`

## Tools Used
- `curl` + grep to pull Google Drive file IDs from the folder HTML
- Web search to confirm campus location and Ba Vì peak heights
- (Intended tool: Google Earth 3D line-of-sight projection)

## Reproduction (Drive download trick)
```bash
curl -sL "https://drive.google.com/drive/folders/<FOLDER_ID>" -A "Mozilla/5.0" -o folder.html
grep -oE '"[a-zA-Z0-9_-]{25,40}"' folder.html | sort -u   # find file IDs
curl -sL "https://drive.google.com/uc?export=download&id=<FILE_ID>" -o img1.jpg
```

## Reasoning Notes
- The campus map image was the decisive clue (no need to actually run Google Earth). Recognizing
  the Vietnamese title + FPT branding immediately fixed the observer location.
- Ba Vì's triple-peak silhouette is the classic landmark visible from the Hòa Lạc plain.
