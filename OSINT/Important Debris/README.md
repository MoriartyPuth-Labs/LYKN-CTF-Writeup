# Important Debris

**Category:** OSINT (MH370 debris research)
**Status:** SOLVED
**Flag:** `LYKN{ITEM31_BAC27WPPS61_BMS4-20}`

## Challenge Description
> "Some MH370 records ... focus ... on fragments recovered years later across the Indian Ocean
> region. One later debris report describes several pieces from Madagascar, and one item stands
> out because investigators could link a small marking to a Boeing cabin component. Find that
> item and recover the item index, the full marker part number, and the Boeing material
> specification referenced in the report."

Flag format: `LYKN{ITEM_MARKER_SPEC}` — e.g. `LYKN{ITEM18_AAA123NN_ABC1-23}`.

## Walkthrough / Reasoning

1. **Identify the piece.** The "several pieces from Madagascar" + "small marking linked to a
   Boeing cabin component" points to the **floor-panel fragment** found near Sandravinany, South
   Madagascar (2018). A partial placard reading `WPPS61` was recovered.

2. **The marker part number.** Independent Group member **Don Thompson** determined the full
   placard part number is **`BAC27WPPS61`**. (Original source: Victor Iannello's
   radiantphysics.com post "New MH370 Debris Suggests a High Speed Impact", and Thompson's own
   "Floor Panel Analysis" PDF.) The placard text: *"REPLACEMENT OF THIS PANEL WITH OTHER THAN
   BMS4-20 WILL REQUIRE MINIMUM 1 MIL FOIL COVERING ON NON-FAYING LOWER SURFACE."*

3. **The Boeing material spec.** From the placard: **`BMS4-20`** (high-strength honeycomb flooring
   panel used in the passenger compartment of commercial aircraft incl. the B777-200ER).

4. **The item INDEX — the tricky part.** First submissions `ITEM3` and `PART3` were **rejected**.
   The radiantphysics blog labels it "Part 3", but the challenge wants the **official item index
   from the Malaysian SIR / ATSB "Debris Examination Report — Identification of Debris recovered
   from Madagascar in 2016, 2017 and 2018" (30 Dec 2018)**. In that official numbering the
   floor-panel piece is **Item 31**:
   > "Item 31: The thickness of the debris and the material it was made of were consistent with
   > that stated on the floor panel manufacturer's (The Gill Corporation) Product Data Sheet which
   > meets the BMS4-20 specification ... Item 31 is likely to be from MH370 ... based on the
   > material it was constructed of and the visible part of the placard which confirms that the
   > debris is a floor panel of a Boeing aircraft."

   (Confirmed via mh370search.com "New Clues" comment thread quoting the official reports; Item 28
   = vertical stabilizer TE panel, Item 29/30/32 = other cabin pieces, **Item 31 = the placard
   floor panel**.)

## Answer Construction
`ITEM31` + `BAC27WPPS61` + `BMS4-20`  ⇒ `LYKN{ITEM31_BAC27WPPS61_BMS4-20}`

## Tools Used
- Web search + WebFetch across: radiantphysics.com, mh370wiki.net, mh370search.com
- `curl` + Python regex to pull raw article/comment text (some pages 403 on WebFetch — used the
  Wayback Machine `web.archive.org/web/<ts>if_/<url>` and Dropbox `?dl=1` for Thompson's PDF)

## Reasoning Notes
- **Item index != informal "Part N".** The key correction was realizing "item index" refers to
  the sequential numbering in the *official Malaysian/ATSB debris examination report*, where the
  Madagascar floor panel is **Item 31**, not the blog's "Part 3".
- Source chain: blog (identifies BAC27WPPS61 / BMS4-20) → Thompson PDF (placard text + provenance,
  cross-referenced to a matching MH17/9M-MRD galley placard) → official SIR item list (Item 31).
