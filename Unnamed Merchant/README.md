# Unnamed Merchant

**Category:** OSINT (MH370 / maritime research)
**Status:** SOLVED
**Flag:** `LYKN{HOEGH_ST_PETERSBURG_9420045_257366000_19_FILIPINO}`

## Challenge Description
> "AMSA's public MH370 timeline records that merchant ships responded to an Australian shipping
> broadcast during the first southern Indian Ocean search phase, but the timeline does not name
> every civilian surface asset. Find the civilian vessel that was closest to the early southern
> Indian Ocean lead and find its IMO, MMSI number, number of crew and their nationality."

Flag format: `LYKN{VESSEL_NAME_IMO_MMSI_NUMBER OF CREW_NATIONALITY}`
Example: `LYKN{EXAMPLE_SHIP_1234567_123456789_36_CANADIAN}`.

## Walkthrough / Reasoning

1. **Identify the vessel.** During the 20 March 2014 first southern-Indian-Ocean phase (AMSA
   Update 7, satellite objects ~2,500 km SW of Perth), the Norwegian Shipowners' Association said
   the car carrier **Höegh St. Petersburg** was the **closest ship** to the reported objects and
   the **first to arrive** in the search area (diverted en route from Madagascar toward Melbourne
   / Western Australia). This matches the "closest civilian vessel to the early lead."

2. **Crew + nationality.** Multiple outlets (Philstar, GMA News) reported an **all-Filipino crew**
   of **19** (incl. a master with 27 years' experience). One source said "20 Filipinos" but the
   detailed reporting says **19**, which is the intended value.

3. **IMO / MMSI.** From maritime databases (MarineTraffic, VesselFinder, MyShipTracking,
   FleetMon — all consistent):
   - **IMO: 9420045**
   - **MMSI: 257366000**
   - Flag: Norway, Call sign LAII7, vehicles carrier, built 2009.

## Answer Construction
`HOEGH_ST_PETERSBURG` + `9420045` + `257366000` + `19` + `FILIPINO`
⇒ `LYKN{HOEGH_ST_PETERSBURG_9420045_257366000_19_FILIPINO}`

## Tools Used
- Web search (news reporting for closest-ship + crew), maritime databases for IMO/MMSI

## Reasoning Notes
- Two data points had ambiguity: the "19 vs 20" crew count (use **19**), and vessel-name spacing
  (flag uses underscores: `HOEGH_ST_PETERSBURG`).
- The vessel is deliberately "unnamed" in AMSA's own timeline — the challenge is to recover the
  civilian asset from press/maritime OSINT rather than the official government record.
