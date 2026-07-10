"""
Step 3: Segment-level brute-force (breakthrough script)

Extracts just the first segment (code between comma 0 and comma 1)
and tests all 256 byte values against it independently.
This is the script that FIRST found the correct value: 76 = 'L'.
"""

with open("output1.txt") as f:
    content = f.read().strip()
tokens = content.split()

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

comma_pos = [i for i, c in enumerate(bf) if c == ',']
seg1 = bf[comma_pos[0] + 1 : comma_pos[1]]
print(f"Segment 1 length: {len(seg1)}")


def emulate_segment(seg, initial_val, max_steps=500000):
    """Run a single segment with initial_val pre-loaded at ptr=150."""
    tape = [0] * 300
    ptr = 150
    tape[ptr] = initial_val

    # bracket matching
    stack = []
    jump = {}
    for i, c in enumerate(seg):
        if c == '[':
            stack.append(i)
        elif c == ']':
            if stack:
                j = stack.pop()
                jump[i] = j
                jump[j] = i
            else:
                return False, 0, tape, ptr  # unmatched bracket

    steps = 0
    ip = 0
    while 0 <= ip < len(seg) and steps < max_steps:
        c = seg[ip]
        if c == '>':
            ptr += 1
        elif c == '<':
            ptr -= 1
        elif c == '+':
            tape[ptr] = (tape[ptr] + 1) & 0xFF
        elif c == '-':
            tape[ptr] = (tape[ptr] - 1) & 0xFF

        if c == '[' and tape[ptr] == 0:
            ip = jump[ip]
        elif c == ']' and tape[ptr] != 0:
            ip = jump[ip]

        steps += 1
        ip += 1

    return ip >= len(seg), steps, tape, ptr


print("Testing all 256 values for segment 1...")
for v in range(256):
    halted, steps, tape, ptr = emulate_segment(seg1, v, max_steps=500000)
    if halted:
        ch = chr(v) if 32 <= v < 127 else f'\\x{v:02x}'
        print(f"  ✓ Value {v} ('{ch}'): HALTED after {steps} steps! "
              f"ptr={ptr} tape[ptr]={tape[ptr]}")
        break
else:
    print("  ✗ No value halted within 500K steps")
