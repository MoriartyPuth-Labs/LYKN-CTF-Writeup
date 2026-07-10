"""
Step 2: Instruction-pointer-level tracer

Runs the full BF program with various inputs and tracks which
instruction pointers are visited, to identify exactly where the
program gets stuck (the validation guard loops).
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


def trace(code, inp, max_steps=200000):
    tape = [0] * 30000
    ptr = 3000
    ip = 0
    inp_pos = 0

    # bracket matching
    stack = []
    bracket_map = {}
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']' and stack:
            j = stack.pop()
            bracket_map[i] = j
            bracket_map[j] = i

    visited_ips = set()
    steps = 0

    while ip < len(code) and steps < max_steps:
        c = code[ip]
        visited_ips.add(ip)

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
                tape[ptr] = ord(inp[inp_pos])
                inp_pos += 1
            else:
                tape[ptr] = 0

        if c == '[' and tape[ptr] == 0:
            ip = bracket_map[ip]
        elif c == ']' and tape[ptr] != 0:
            ip = bracket_map[ip]

        steps += 1
        ip += 1

    return {
        'halted': ip >= len(code),
        'steps': steps,
        'final_ip': ip,
        'visited_ips': visited_ips,
        'input_consumed': inp_pos,
        'ptr': ptr,
    }


# Test with null bytes
result = trace(bf, "\x00" * 34, 100000)
print(f"Input: null bytes")
print(f"  halted: {result['halted']}")
print(f"  steps: {result['steps']}")
print(f"  final_ip: {result['final_ip']}")
print(f"  consumed: {result['input_consumed']}")

# Show the last visited IPs before timeout
visited = sorted(result['visited_ips'])
last_ips = visited[-30:]
print(f"\n  Last 30 IPs visited:")
for ip in last_ips:
    ctx = bf[max(0, ip - 5):ip + 6]
    print(f"    IP {ip}: '{bf[ip]}'  ctx: ...{ctx}...")

# Locate the [><] guard
guard_pos = bf.find("[><]")
print(f"\n  First [><] guard at position: {guard_pos}")
print(f"  Code around guard: ...{bf[guard_pos-10:guard_pos+15]}...")

# Check if execution passed through the guard
if guard_pos in result['visited_ips']:
    print(f"  → Execution REACHED the guard (but cell ≠ 0 → infinite loop)")
else:
    print(f"  → Execution never reached the guard")
