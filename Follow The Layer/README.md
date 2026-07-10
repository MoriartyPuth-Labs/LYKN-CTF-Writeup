# Follow The Layer

**Category:** OSINT / Blockchain (Tron USDT tracing)
**Status:** SOLVED
**Flag:** `LYKNCTF{7e401f8004084d4bf9f792535fdf5b89138a935d027b6b75ceb2dd3ac8838fab:03/21/2025:FUNNULL}`
**Flag format:** `LYKNCTF{tx_hash:MM/DD/YYYY:ENTITY}` (example: `LYKNCTF{a1b2c3...f64:01/15/2025:BINANCE}`)

Accepted answer components:
- **tx_hash** = `7e401f8004084d4bf9f792535fdf5b89138a935d027b6b75ceb2dd3ac8838fab`
  (hop 3: passthrough `TQMq9s5e…Do3tb` → `TJ7hhYhV…L3JSdb` "Bitget 9" — the last on-chain hop
  before funds enter the exchange and become unattributable)
- **date** = `03/21/2025`
- **entity** = `FUNNULL` (the OFAC-sanctioned owner of the collection-hub wallet
  `TNmRfnSUXZoWWzxcDDbf95eGQYXt1mJDt8`)

## Challenge Description
> "Our fraud response team flagged a suspicious USDT transfer linked to an online scam operation.
> The payment trail starts here:
> `d4500023a8114caaa640ab92bb8f73830a5303ccdfc4e9b0cf862bdae7ae336b`
> The money ... was layered through a series of wallets before disappearing into the shadows...
> 1. What is the transaction hash of the last traceable hop?
> 2. What date did it occur? (MM/DD/YYYY)
> 3. What is the name of the sanctioned entity at the heart of this operation?"

## Network / Tooling
- This is a **Tron (TRC-20 USDT)** transaction, not Ethereum. USDT contract
  `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`.
- Traced entirely with the **TronScan public API** via `curl` + Python `json`:
  - `https://apilist.tronscanapi.com/api/transaction-info?hash=<TXID>`
  - `https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&sort=-timestamp&relatedAddress=<ADDR>`
  - `https://apilist.tronscanapi.com/api/account?address=<ADDR>`
- `curl` direct + `json.load` is far more reliable/precise than WebFetch summaries (which
  mis-stated a timestamp early on).

## The Trace (chain of hops)

| Hop | Tx hash (prefix) | From → To | Amount | Date (UTC) |
|-----|------------------|-----------|--------|------------|
| 1 (given) | `d4500023…ae336b` | `TXk7Dor9…4BcwX` → `TNmRfnSU…1mJDt8` | 2,700 USDT | 2025-02-27 |
| 2 | `2ef09557…56b9d9` | `TNmRfnSU…1mJDt8` (hub) → `TQMq9s5e…Do3tb` | 5,222 USDT | 2025-03-21 |
| 3 | `7e401f80…838fab` | `TQMq9s5e…Do3tb` (passthrough) → `TJ7hhYhV…L3JSdb` | 5,222 USDT | 2025-03-21 |

- **`TNmRfnSUXZoWWzxcDDbf95eGQYXt1mJDt8`** = the scam **collection hub** (386 tiny inbound
  deposits — classic pig-butchering funnel — periodically swept out in lump sums). This address is
  the **OFAC-sanctioned wallet of Funnull Technology Inc.** (sanctioned 29 May 2025; confirmed via
  Chainalysis' Funnull writeup, which lists the ETH addr `0xd5ED34…d510` and the TRX addr
  `TNmRfnSUXZoWWzxcDDbf95eGQYXt1mJDt8`).
- **`TQMq9s5eqxzHW9CG4hgrWxVZaz4oZDo3tb`** = pure **pass-through / layering** wallet (receives and
  forwards the identical amount within minutes; no tag).
- **`TJ7hhYhVhaxNx6BPyq7yFpqZrQULL3JSdb`** = the only **TronScan-tagged** address in the chain:
  **"Bitget 9"** — a Bitget exchange deposit hot wallet. This is where on-chain attribution ends
  (funds enter a CEX's commingled reserves).

## Interpretation / Reasoning (final)
- **Entity** "at the heart of the operation" = **FUNNULL** — the hub wallet
  `TNmRfnSUXZoWWzxcDDbf95eGQYXt1mJDt8` is OFAC-sanctioned and attributed to Funnull Technology Inc.
- **Last traceable hop** = the hop where funds leave the layering wallets and enter the exchange:
  hop 3, tx `7e401f80…838fab`, passthrough → **Bitget** deposit wallet, on **03/21/2025**. Once in
  Bitget's commingled reserves, on-chain tracing stops — so the Bitget-deposit tx (not Bitget
  itself as "entity", and not the earlier hub sweep) is the "last traceable hop".
- The winning combination is therefore the **Bitget-deposit tx hash + its date + FUNNULL as the
  entity**. (Same string that had been tried in-session; recorded here as the confirmed accepted
  answer.)

## Tools Used
- `curl`, Python 3.11 (`json`, `datetime`), TronScan API
- Chainalysis / OFAC SDN reporting to attribute the hub wallet to Funnull

## Reproduction (fetch a hop)
```bash
curl -s "https://apilist.tronscanapi.com/api/transaction-info?hash=d4500023a8114caaa640ab92bb8f73830a5303ccdfc4e9b0cf862bdae7ae336b" | python -m json.tool
curl -s "https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&sort=-timestamp&relatedAddress=TNmRfnSUXZoWWzxcDDbf95eGQYXt1mJDt8"
curl -s "https://apilist.tronscanapi.com/api/account?address=TJ7hhYhVhaxNx6BPyq7yFpqZrQULL3JSdb"   # addressTag: "Bitget 9"
```
