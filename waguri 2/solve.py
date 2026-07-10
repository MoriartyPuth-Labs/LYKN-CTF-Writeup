"""
Waguri 2 — LYKN CTF Brainfuck Reverse Engineering Challenge Solver

Reads output1.txt containing 23,000 character-name tokens,
maps them to Brainfuck commands, brute-forces each of the 34
input segments to find the correct byte value, and outputs the flag.

Usage: python solve.py < output1.txt
"""

import sys

# ============================================================
# Step 1: Load and map tokens to Brainfuck
# ============================================================

with open("output1.txt") as f:
    content = f.read().strip()
tokens = content.split()

# Mapping B — confirmed by pattern analysis of BF idioms
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

# ============================================================
# Step 2: Extract segments between commas
# ============================================================

comma_positions = [i for i, c in enumerate(bf) if c == ',']
print(f"[*] Total commas: {len(comma_positions)}", file=sys.stderr)

# Each segment is the code between comma N and comma N+1
segments = []
for i in range(len(comma_positions) - 1):
    segments.append(bf[comma_positions[i] + 1 : comma_positions[i + 1]])
# Last segment: code after the final comma
segments.append(bf[comma_positions[-1] + 1 :])

print(f"[*] Extracted {len(segments)} segments", file=sys.stderr)

# ============================================================
# Step 3: For each segment, find which byte value makes it halt
# ============================================================

def find_halt_value(segment, max_steps=500000):
    """Test all 256 byte values against a segment. Return the first
    value that makes the segment complete (ip reaches end), or None."""

    # Pre-compute bracket jumps for this segment
    stack = []
    jump = {}
    for i, c in enumerate(segment):
        if c == '[':
            stack.append(i)
        elif c == ']' and stack:
            j = stack.pop()
            jump[i] = j
            jump[j] = i

    for value in range(256):
        tape = [0] * 300
        ptr = 150
        tape[ptr] = value  # seed the input byte

        steps = 0
        ip = 0

        while 0 <= ip < len(segment) and steps < max_steps:
            c = segment[ip]

            if c == '>':
                ptr += 1
            elif c == '<':
                ptr -= 1
            elif c == '+':
                tape[ptr] = (tape[ptr] + 1) & 0xFF
            elif c == '-':
                tape[ptr] = (tape[ptr] - 1) & 0xFF

            # Handle loops
            if c == '[' and tape[ptr] == 0:
                ip = jump.get(ip, ip)
            elif c == ']' and tape[ptr] != 0:
                ip = jump.get(ip, ip)

            steps += 1
            ip += 1

        if ip >= len(segment):
            return value

    return None


input_values = []
for idx, seg in enumerate(segments):
    val = find_halt_value(seg)
    if val is None:
        print(f"[-] Segment {idx}: NO VALUE FOUND (max_steps exceeded)", file=sys.stderr)
        sys.exit(1)
    ch = chr(val) if 32 <= val < 127 else f'\\x{val:02x}'
    print(f"[+] Segment {idx:2d}: value={val:3d} ('{ch}')", file=sys.stderr)
    input_values.append(val)

# ============================================================
# Step 4: Build and print the flag
# ============================================================

flag = ''.join(chr(v) for v in input_values)
print(f"\nFlag: {flag}")

# ============================================================
# Step 5: Verify — run the full BF program with the discovered input
# ============================================================

print("\n[*] Verifying full BF program...", file=sys.stderr)

tape = [0] * 30000
ptr = 3000
inp_pos = 0

# Pre-compute bracket jumps for the full program
stack = []
jump = {}
for i, c in enumerate(bf):
    if c == '[':
        stack.append(i)
    elif c == ']':
        j = stack.pop()
        jump[i] = j
        jump[j] = i

steps = 0
ip = 0
max_steps = 50000000

while 0 <= ip < len(bf) and steps < max_steps:
    c = bf[ip]

    if c == '>':
        ptr += 1
    elif c == '<':
        ptr -= 1
    elif c == '+':
        tape[ptr] = (tape[ptr] + 1) & 0xFF
    elif c == '-':
        tape[ptr] = (tape[ptr] - 1) & 0xFF
    elif c == ',':
        if inp_pos < len(input_values):
            tape[ptr] = input_values[inp_pos]
            inp_pos += 1
        else:
            tape[ptr] = 0

    if c == '[' and tape[ptr] == 0:
        ip = jump[ip]
    elif c == ']' and tape[ptr] != 0:
        ip = jump[ip]

    steps += 1
    ip += 1

halted = ip >= len(bf)
print(f"[*] Verification: halted={halted}, steps={steps}, consumed={inp_pos}/34", file=sys.stderr)

if halted:
    print("\n✓ Solution verified! Flag:", flag, file=sys.stderr)
else:
    print("\n✗ Program did not halt — something is wrong", file=sys.stderr)
    sys.exit(1)
