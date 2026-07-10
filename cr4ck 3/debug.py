#!/usr/bin/env python3
"""Debug the VM emulator step by step for position 0."""

R9 = bytes([
    0xd0, 0xcc, 0x41, 0x3b, 0x99, 0x6e, 0x2d, 0xc1,
    0xe7, 0xc4, 0x67, 0xfa, 0xb7, 0x71, 0x45, 0xae,
    0x85, 0x02, 0xe8, 0xac, 0xea, 0x62, 0x66, 0x16,
    0xff, 0xa7, 0xd0, 0xf4, 0xf4, 0x65, 0xe4, 0x97,
    0x6b, 0x8f, 0x82, 0x51, 0xd4, 0x59, 0x36, 0x6b,
    0xab, 0x23, 0x2c, 0x96, 0xbd, 0xc9, 0xec, 0x0d,
    0xf4, 0x18, 0x9b, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x6e, 0x52, 0x33, 0xbb, 0x7f, 0x41, 0xd4, 0x11,
    0xf9, 0xce, 0xaf, 0x9c, 0xf1, 0xbd, 0x23, 0x36,
    0x7c, 0x33, 0x3c, 0xe8, 0x0b, 0xc2, 0x5c, 0x91,
    0x64, 0x26, 0x95, 0xc4, 0xc4, 0x70, 0xb0, 0xbf,
    0xd2, 0x8b, 0x6a, 0x71, 0x81, 0x20, 0x22, 0xb4,
    0xe5, 0x8a, 0x77, 0x2a, 0xf9, 0xb1, 0x9e, 0xdd,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x98, 0x2f, 0x8a, 0x42, 0x91, 0x44, 0x37, 0x71,
    0xcf, 0xfb, 0xc0, 0xb5, 0xa5, 0xdb, 0xb5, 0xe9,
    0x5b, 0xc2, 0x56, 0x39, 0xf1, 0x11, 0xf1, 0x59,
    0xa4, 0x82, 0x3f, 0x92, 0xd5, 0x5e, 0x1c, 0xab,
    0x98, 0xaa, 0x07, 0xd8, 0x01, 0x5b, 0x83, 0x12,
    0xbe, 0x85, 0x31, 0x24, 0xc3, 0x7d, 0x0c, 0x55,
    0x74, 0x5d, 0xbe, 0x72, 0xfe, 0xb1, 0xde, 0x80,
    0xa7, 0x06, 0xdc, 0x9b, 0x74, 0xf1, 0x9b, 0xc1,
])

def rol32(v, n):
    n &= 31
    return ((v << n) | (v >> (32 - n))) & 0xFFFFFFFF

def imul32(a, b):
    return (a * b) & 0xFFFFFFFF

def step_emu(input_byte, char_index, r15d_in, stack_78_in):
    eax = 0xC0DE1234
    state = [0]*8
    edx = 0
    r11d = 0xFFFFFFD0
    r12d = input_byte
    r8d = 0
    r14d = 0x186A0
    r15d = r15d_in
    stack_78 = stack_78_in
    stack_80 = 0
    base = char_index * 8
    first = True
    step = 0

    while True:
        step += 1
        if not first:
            if edx > 0x32:
                print(f"FAIL after step {step}: edx {edx} > 0x32")
                return (0xFFFFFFFF, r15d, stack_78)
            r14d -= 1
            if r14d == 0:
                print(f"FAIL after step {step}: r14d=0")
                return (0xFFFFFFFF, r15d, stack_78)
            r11d = R9[base + edx]
        first = False

        # dispatch
        ecx = (eax >> 24) & 0xFF
        x = ecx ^ r11d
        r11d_save = x & 0xFF
        ecx = ((x - 0x10) & 0xFF)

        if ecx > 0x10:
            print(f"FAIL step {step}: handler idx {ecx} > 0x10 (eax>>24={(eax>>24)&0xFF:#04x} r11d={r11d:#x})")
            return (0xFFFFFFFF, r15d, stack_78)

        eax = (eax ^ r11d_save) & 0xFFFFFFFF
        r11d = (edx + 1) & 0xFFFFFFFF
        eax = rol32(eax, 0xB)
        eax = imul32(eax, 0x9c5ab3d7)
        eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        handler = ecx
        print(f"Step {step}: EAX={eax:#010x} EDX={edx} R11={r11d:#x} h={handler}")
        if handler <= 2 or handler >= 14:
            print(f"  state={[f'{s:#010x}' for s in state]}")

        if handler == 0:
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            edx += 2
            eax = (eax ^ op_r) & 0xFFFFFFFF
            r11d = op_r
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            idx = r11d & 7
            print(f"  H0: state[{idx}] = stack_78({stack_78:#x}), op1=0x{op1:02x} op_r=0x{op_r:02x}")
            state[idx] = stack_78
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 1:
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            edx += 2
            eax = (eax ^ op_r) & 0xFFFFFFFF
            r11d = op_r
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            idx = r11d & 7
            state[idx] = r12d
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H1: state[{idx}] = r12d({r12d:#x})")

        elif handler == 2:
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            edx += 2
            eax = (eax ^ op_r) & 0xFFFFFFFF
            r11d = op_r
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            idx = r11d & 7
            state[idx] = r15d
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 3:
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            saved_op1 = op_r
            saved_edx = edx
            eax = (eax ^ op_r) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            data_ptr = saved_edx + 2
            bit_count = 0
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            ebx = 0
            for _ in range(4):
                t = eax
                data_ptr += 1
                t = (t >> 24) & 0xFF
                t ^= R9[base + data_ptr - 1]
                eax = (eax ^ t) & 0xFFFFFFFF
                t = (t << (bit_count & 31)) & 0xFFFFFFFF
                bit_count += 8
                eax = rol32(eax, 0xB)
                ebx = (ebx | t) & 0xFFFFFFFF
                eax = imul32(eax, 0x9c5ab3d7)
                eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            idx = saved_op1 & 7
            edx = saved_edx + 6
            print(f"  H3: state[{idx}] = {ebx:#010x}")
            state[idx] = ebx

        elif handler == 4:
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF
            op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF
            eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx2 = op_r2 & 7
            idx1 = saved_r11 & 7
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            state[idx1] = state[idx2]
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H4: state[{idx1}] = state[{idx2}]({state[idx2]:#010x})")

        elif handler == 5:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1; eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx2 = op_r2 & 7; idx1 = saved_r11 & 7
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            a = state[idx1]; b = state[idx2]
            state[idx1] = (a + b) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H5: state[{idx1}] += state[{idx2}] → {state[idx1]:#010x}")

        elif handler == 6:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1; eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx2 = op_r2 & 7; idx1 = saved_r11 & 7
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            a = state[idx1]; b = state[idx2]
            state[idx1] = (a - b) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H6: state[{idx1}] -= state[{idx2}] → {state[idx1]:#010x}")

        elif handler == 7:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1; eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx2 = op_r2 & 7; idx1 = saved_r11 & 7
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            a = state[idx1]; b = state[idx2]
            state[idx1] = (a ^ b) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H7: state[{idx1}] ^= state[{idx2}] → {state[idx1]:#010x}")

        elif handler == 8:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1; eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx2 = op_r2 & 7; idx1 = saved_r11 & 7
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            a = state[idx1]; b = state[idx2]
            state[idx1] = imul32(a, b)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H8: state[{idx1}] *= state[{idx2}] → {state[idx1]:#010x}")

        elif handler == 9:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r = (op1 ^ c) & 0xFF
            saved_op1 = op_r; saved_edx = edx
            eax = (eax ^ op_r) & 0xFFFFFFFF; eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            data_ptr = saved_edx + 2; bit_count = 0
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF; ebx = 0
            for _ in range(4):
                t = eax; data_ptr += 1; t = (t >> 24) & 0xFF; t ^= R9[base + data_ptr - 1]
                eax = (eax ^ t) & 0xFFFFFFFF; t = (t << (bit_count & 31)) & 0xFFFFFFFF
                bit_count += 8; eax = rol32(eax, 0xB); ebx = (ebx | t) & 0xFFFFFFFF
                eax = imul32(eax, 0x9c5ab3d7); eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            idx = saved_op1 & 7; edx = saved_edx + 6
            print(f"  H9: state[{idx}] *= {ebx:#010x} (was {state[idx]:#010x})")
            state[idx] = imul32(state[idx], ebx)

        elif handler == 10:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r = (op1 ^ c) & 0xFF
            saved_op1 = op_r; saved_edx = edx
            eax = (eax ^ op_r) & 0xFFFFFFFF; eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            data_ptr = saved_edx + 2; bit_count = 0
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF; edx_acc = 0
            r11_ptr = base + data_ptr
            for _ in range(4):
                t = eax; r11_ptr += 1; t = (t >> 24) & 0xFF; t ^= R9[r11_ptr - 1]
                eax = (eax ^ t) & 0xFFFFFFFF; t = (t << (bit_count & 31)) & 0xFFFFFFFF
                bit_count += 8; eax = rol32(eax, 0xB); edx_acc = (edx_acc | t) & 0xFFFFFFFF
                eax = imul32(eax, 0x9c5ab3d7); eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            idx = saved_op1 & 7; edx = saved_edx + 6
            print(f"  H10: state[{idx}] += {edx_acc:#010x} (was {state[idx]:#010x})")
            state[idx] = (state[idx] + edx_acc) & 0xFFFFFFFF

        elif handler == 11:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r = (op1 ^ c) & 0xFF
            saved_op1 = op_r; saved_edx = edx
            eax = (eax ^ op_r) & 0xFFFFFFFF; eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            data_ptr = saved_edx + 2; bit_count = 0
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF; edx_acc = 0
            r11_ptr = base + data_ptr
            for _ in range(4):
                t = eax; r11_ptr += 1; t = (t >> 24) & 0xFF; t ^= R9[r11_ptr - 1]
                eax = (eax ^ t) & 0xFFFFFFFF; t = (t << (bit_count & 31)) & 0xFFFFFFFF
                bit_count += 8; eax = rol32(eax, 0xB); edx_acc = (edx_acc | t) & 0xFFFFFFFF
                eax = imul32(eax, 0x9c5ab3d7); eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            idx = saved_op1 & 7; edx = saved_edx + 6
            print(f"  H11: state[{idx}] ^= {edx_acc:#010x} (was {state[idx]:#010x})")
            state[idx] = (state[idx] ^ edx_acc) & 0xFFFFFFFF

        elif handler == 12:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF; eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx1 = saved_r11 & 7; shift = op_r2 & 31
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            state[idx1] = rol32(state[idx1], shift)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H12: ROL state[{idx1}] by {shift} → {state[idx1]:#010x}")

        elif handler == 13:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF; eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx1 = saved_r11 & 7; shift = (-op_r2) & 31
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            state[idx1] = rol32(state[idx1], shift)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H13: ROR state[{idx1}] by {(-shift)&31} → {state[idx1]:#010x}")

        elif handler == 14:
            op1 = R9[base + r11d]; c = (eax >> 24) & 0xFF; op_r1 = (op1 ^ c) & 0xFF
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF; eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF; op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF; eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx1 = saved_r11 & 7; shift = op_r2 & 31
            eax = rol32(eax, 0xB); eax = imul32(eax, 0x9c5ab3d7)
            val = state[idx1]
            state[idx1] = (val ^ (val >> shift)) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H14: state[{idx1}] ^= (state>>{shift}) → {state[idx1]:#010x}")

        elif handler == 15:
            op1 = R9[base + r11d]
            r8d = eax
            c = (r8d >> 24) & 0xFF
            op_r = (c ^ op1) & 0xFF
            ecx = op_r
            r8d = op_r & 7
            eax = (eax ^ ecx) & 0xFFFFFFFF
            r8d = state[r8d]
            edx += 2
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            print(f"  H15: r8d = state[{op_r & 7}] = {r8d:#010x}")
            # falls through to epilogue

        elif handler == 16:
            print(f"  H16: r8d & 0xFFFF = {r8d & 0xFFFF:#06x}, expected = {EXPECTED[char_index]:#06x}")
            stack_78 = r8d
            if (r8d & 0xFFFF) != EXPECTED[char_index]:
                return (0xFFFFFFFF, r15d, stack_78)
            eax = imul32(r15d, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            eax = rol32(eax, 0xD)
            r15d = eax
            return (r8d & 0xFFFF, r15d, stack_78)

EXPECTED = [0x526e, 0xbb33, 0x417f, 0x11d4, 0xcef9, 0x9caf,
            0xbdf1, 0x3623, 0x337c, 0xe83c, 0xc20b, 0x915c,
            0x2664, 0xc495, 0x70c4, 0xbfb0, 0x8bd2, 0x716a,
            0x2081, 0xb422, 0x8ae5, 0x2a77, 0xb1f9, 0xdd9e]

print("Testing 'A' at position 0:")
result, r15d, s78 = step_emu(ord('A'), 0, 0, 0)
print(f"\nResult: r8d_low={result:#06x}")
