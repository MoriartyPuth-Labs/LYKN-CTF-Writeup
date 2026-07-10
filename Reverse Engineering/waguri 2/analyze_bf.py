"""
Step 1: Token counting & BF structural analysis

Counts occurrences of each character name token,
converts to BF using Mapping B, and analyzes loop patterns
to confirm the mapping is correct.
"""

with open("output1.txt") as f:
    content = f.read().strip()
tokens = content.split()

# ---- Token counting ----
from collections import Counter
counts = Counter(tokens)
print("=== Token Counts ===")
for token, cnt in counts.most_common():
    print(f"  {token}: {cnt}")
print(f"  Total: {sum(counts.values())}")
print()

# ---- Mapping B ----
mapping = {
    'usami_shohei': '>',
    'natsusawa_saku': '<',
    'tsumugi_rintaro': '-',
    'waguri_kaoruko': '+',
    'kaoru_hana': ',',
    'yorita_ayato': '[',
    'hoshina_subaru': ']',
}
bf = ''.join(mapping[t] for t in tokens)
print(f"BF program length: {len(bf)}")
print(f"First 200 chars: {bf[:200]}")
print()

# ---- Loop pattern analysis ----
def get_loops(code):
    stack = []
    jump = {}
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            j = stack.pop()
            jump[i] = j
            jump[j] = i

    loops = []
    for i in range(len(code)):
        if code[i] == '[':
            body = code[i+1:jump[i]]
            if len(body) <= 80:   # only short loops for readability
                loops.append(body)
    return loops

loop_counts = Counter(get_loops(bf))
print("=== Top Loop Patterns (Mapping B) ===")
for body, cnt in loop_counts.most_common(20):
    print(f"  [{body}] x{cnt}")
print()

# ---- Comma positions (input reads) ----
comma_positions = [i for i, c in enumerate(bf) if c == ',']
print(f"=== Commas: {len(comma_positions)} total ===")
for i, pos in enumerate(comma_positions[:5]):
    ctx = bf[max(0,pos-20):pos+20]
    print(f"  #{i} at pos {pos}: ...{ctx}...")
