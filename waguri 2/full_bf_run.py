"""
Step 4: Full program test & last-segment discovery

After finding that segment 0 accepts 'L', we test the full program
with all 'L's. It doesn't halt because later segments expect different
values. This script probes the last segment and discovers value 125 = '}'.
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


def run_bf(code, inp, max_steps=50000000):
    tape = [0] * 30000
    ptr = 3000
    inp_pos = 0

    stack = []
    jump = {}
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            j = stack.pop()
            jump[i] = j
            jump[j] = i

    steps = 0
    ip = 0
    while 0 <= ip < len(code) and steps < max_steps:
        c = code[ip]
        if c == '>':
            ptr += 1
        elif c == '<':
            ptr -= 1
        elif c == '+':
            tape[ptr] = (tape[ptr] + 1) & 0xFF
        elif c == '-':
            tape[ptr] = (tape[ptr] - 1) & 0xFF
        elif c == ',':
            if inp_pos < len(inp):
                tape[ptr] = inp[inp_pos]
                inp_pos += 1
            else:
                tape[ptr] = 0

        if c == '[' and tape[ptr] == 0:
            ip = jump[ip]
        elif c == ']' and tape[ptr] != 0:
            ip = jump[ip]

        steps += 1
        ip += 1

    return ip >= len(code), steps, inp_pos


# Test with all 'L's
print("Testing full BF with 'L' * 34...")
halted, steps, consumed = run_bf(bf, [76] * 34, max_steps=10000000)
print(f"  halted={halted}, steps={steps}, consumed={consumed}")

# Extract the last segment and find its accepting value
comma_pos = [i for i, c in enumerate(bf) if c == ',']
last_seg = bf[comma_pos[-1] + 1:]
print(f"\nLast segment length: {len(last_seg)}")


def test_segment(seg, val, max_steps=200000):
    tape = [0] * 300
    ptr = 150
    tape[ptr] = val

    stack = []
    jump = {}
    for i, c in enumerate(seg):
        if c == '[':
            stack.append(i)
        elif c == ']':
            j = stack.pop()
            jump[i] = j
            jump[j] = i

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

    return ip >= len(seg), steps


print("Searching for last segment's accepting value...")
for v in range(256):
    h, s = test_segment(last_seg, v)
    if h:
        ch = chr(v) if 32 <= v < 127 else f'\\x{v:02x}'
        print(f"  ✓ Value {v} ('{ch}') halts in {s} steps")
        break
else:
    print("  ✗ No value found")
