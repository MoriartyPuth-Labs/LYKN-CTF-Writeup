#!/usr/bin/env python3
"""Complete VM emulator + brute-forcer for Serial.exe"""

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

EXPECTED = [0x526e, 0xbb33, 0x417f, 0x11d4, 0xcef9, 0x9caf,
            0xbdf1, 0x3623, 0x337c, 0xe83c, 0xc20b, 0x915c,
            0x2664, 0xc495, 0x70c4, 0xbfb0, 0x8bd2, 0x716a,
            0x2081, 0xb422, 0x8ae5, 0x2a77, 0xb1f9, 0xdd9e]


def rol32(v, n):
    n &= 31
    return ((v << n) | (v >> (32 - n))) & 0xFFFFFFFF

def imul32(a, b):
    return (a * b) & 0xFFFFFFFF


def emulate_char(input_byte, char_index, r15d_in, stack_78_in):
    eax = 0xC0DE1234
    state = [0] * 8
    edx = 0
    r11d = 0xFFFFFFD0
    r12d = input_byte
    r8d = 0
    r14d = 0x186A0
    r15d = r15d_in
    stack_78 = stack_78_in
    stack_80 = 0
    base = 0
    first = True

    while True:
        # --- epilogue (0x2050) — skip on first call ---
        if not first:
            if edx > 0x32:
                return (0xFFFFFFFF, r15d, stack_78)
            r14d -= 1
            if r14d == 0:
                return (0xFFFFFFFF, r15d, stack_78)
            r11d = R9[base + edx]
        first = False

        # --- dispatch (0x1FB0) ---
        if r11d != 0xFFFFFFD0:
            pass  # r11d already loaded from r9 above
        # else: first dispatch, r11d = 0xFFFFFFD0

        ecx = (eax >> 24) & 0xFF
        ecx = (ecx ^ r11d) & 0xFF
        r11d_save = ecx
        ecx = (ecx - 0x10) & 0xFF
        if ecx > 0x10:
            return (0xFFFFFFFF, r15d, stack_78)

        eax = (eax ^ r11d_save) & 0xFFFFFFFF
        r11d = (edx + 1) & 0xFFFFFFFF
        eax = rol32(eax, 0xB)
        eax = imul32(eax, 0x9c5ab3d7)
        eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        handler = ecx

        # ============ HANDLERS ============

        if handler == 0:  # H0: state[op1 & 7] = stack_78
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            edx += 2
            eax = (eax ^ op_r) & 0xFFFFFFFF
            r11d = op_r
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            idx = r11d & 7
            state[idx] = stack_78
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 1:  # H1: state[op1 & 7] = r12d (input byte)
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

        elif handler == 2:  # H2: state[op1 & 7] = r15d
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

        elif handler == 3:  # H3: loop → ebx → state[op1 & 7] = ebx
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            saved_op1 = op_r
            saved_edx = edx
            edx += 2
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
            state[idx] = ebx

        elif handler == 4:  # H4: state[op1 & 7] = state[op2 & 7]
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
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

        elif handler == 5:  # H5: state[op1 & 7] += state[op2 & 7]
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
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
            a = state[idx1]
            b = state[idx2]
            state[idx1] = (a + b) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 6:  # H6: state[op1 & 7] -= state[op2 & 7]
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
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
            a = state[idx1]
            b = state[idx2]
            state[idx1] = (a - b) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 7:  # H7: state[op1 & 7] ^= state[op2 & 7]
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
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
            a = state[idx1]
            b = state[idx2]
            state[idx1] = (a ^ b) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 8:  # H8: state[op1 & 7] *= state[op2 & 7]
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
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
            a = state[idx1]
            b = state[idx2]
            state[idx1] = imul32(a, b)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 9:  # H9: loop → ebx → state[op1 & 7] *= ebx
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            saved_op1_byte = op_r
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
            idx = saved_op1_byte & 7
            edx = saved_edx + 6
            state[idx] = imul32(state[idx], ebx)

        elif handler == 10:  # H10: loop → edx → state[op1 & 7] += edx
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            saved_op1_byte = op_r
            saved_edx = edx
            stack_80 = edx
            edx = 0
            eax = (eax ^ op_r) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            data_ptr = saved_edx + 2
            bit_count = 0
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            edx_acc = 0
            r11_ptr = base + data_ptr
            for _ in range(4):
                t = eax
                r11_ptr += 1
                t = (t >> 24) & 0xFF
                t ^= R9[r11_ptr - 1]
                eax = (eax ^ t) & 0xFFFFFFFF
                t = (t << (bit_count & 31)) & 0xFFFFFFFF
                bit_count += 8
                eax = rol32(eax, 0xB)
                edx_acc = (edx_acc | t) & 0xFFFFFFFF
                eax = imul32(eax, 0x9c5ab3d7)
                eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            idx = saved_op1_byte & 7
            edx = saved_edx + 6
            state[idx] = (state[idx] + edx_acc) & 0xFFFFFFFF

        elif handler == 11:  # H11: loop → edx → state[op1 & 7] ^= edx
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r = (op1 ^ c) & 0xFF
            saved_op1_byte = op_r
            saved_edx = edx
            stack_80 = edx
            edx = 0
            eax = (eax ^ op_r) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            data_ptr = saved_edx + 2
            bit_count = 0
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            edx_acc = 0
            r11_ptr = base + data_ptr
            for _ in range(4):
                t = eax
                r11_ptr += 1
                t = (t >> 24) & 0xFF
                t ^= R9[r11_ptr - 1]
                eax = (eax ^ t) & 0xFFFFFFFF
                t = (t << (bit_count & 31)) & 0xFFFFFFFF
                bit_count += 8
                eax = rol32(eax, 0xB)
                edx_acc = (edx_acc | t) & 0xFFFFFFFF
                eax = imul32(eax, 0x9c5ab3d7)
                eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            idx = saved_op1_byte & 7
            edx = saved_edx + 6
            state[idx] = (state[idx] ^ edx_acc) & 0xFFFFFFFF

        elif handler == 12:  # H12: ROL state[op1 & 7], cl
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFffFFff
            c2 = (eax >> 24) & 0xFF
            op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF
            eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx1 = saved_r11 & 7
            shift = op_r2 & 31
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            state[idx1] = rol32(state[idx1], shift)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 13:  # H13: ROR state[op1 & 7], cl (via neg + rol)
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF
            op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF
            eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx1 = saved_r11 & 7
            shift = (-op_r2) & 31
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            state[idx1] = rol32(state[idx1], shift)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 14:  # H14: state[op1 & 7] ^= (state >> cl)
            op1 = R9[base + r11d]
            c = (eax >> 24) & 0xFF
            op_r1 = (op1 ^ c) & 0xFF
            edx += 3
            saved_r11 = op_r1
            eax = (eax ^ op_r1) & 0xFFFFFFFF
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            c2 = (eax >> 24) & 0xFF
            op2_byte = R9[base + (edx - 1)]
            op_r2 = (op2_byte ^ c2) & 0xFF
            eax = (eax ^ op_r2) & 0xFFFFFFFF
            idx1 = saved_r11 & 7
            shift = op_r2 & 31
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            val = state[idx1]
            state[idx1] = (val ^ (val >> shift)) & 0xFFFFFFFF
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 15:  # H15: r8d = state[op1 & 7]
            op1 = R9[base + r11d]
            r8d = eax
            edx += 2
            c = (r8d >> 24) & 0xFF
            op_r = (c ^ op1) & 0xFF
            ecx = op_r
            r8d = op_r & 7
            eax = (eax ^ ecx) & 0xFFFFFFFF
            r8d = state[r8d]
            eax = rol32(eax, 0xB)
            eax = imul32(eax, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF

        elif handler == 16:  # H16: compare r8d & 0xFFFF vs expected
            stack_78 = r8d
            if (r8d & 0xFFFF) != EXPECTED[char_index]:
                return (0xFFFFFFFF, r15d, stack_78)
            eax = imul32(r15d, 0x9c5ab3d7)
            eax = (eax + 0x3f1e5c2b) & 0xFFFFFFFF
            eax = rol32(eax, 0xD)
            r15d = eax
            return (r8d & 0xFFFF, r15d, stack_78)


def brute_force():
    r15d = 0xc499790f
    s78 = 0
    serial = []
    for pos in range(24):
        found = False
        for ch in range(0x20, 0x7F):
            result, r15d_out, s78_out = emulate_char(ch, pos, r15d, s78)
            if result != 0xFFFFFFFF:
                print(f"  pos {pos}: char '{chr(ch)}' (0x{ch:02x}) → r8d_low=0x{result:04x} R15={r15d_out:08x} S78={s78_out:08x}")
                serial.append(chr(ch))
                r15d = r15d_out
                s78 = s78_out
                found = True
                break
        if not found:
            print(f"  pos {pos}: NO matching char found!")
            break
    if len(serial) == 24:
        print(f"\nSERIAL: {''.join(serial)}")
    return serial


if __name__ == "__main__":
    print("Brute-forcing serial...")
    serial = brute_force()
