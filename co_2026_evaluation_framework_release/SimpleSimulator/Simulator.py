import sys

STACK_START, STACK_END = 0x100, 0x17F
DATA_START, DATA_END = 0x10000, 0x1007F

MAX_INSTRUCTIONS = 64
MAX_STEPS = 200000

HALT_INSTR = "00000000000000000000000001100011"

def bin_to_signed(b):
    x = int(b, 2)
    return x - (1 << len(b)) if b[0] == "1" else x


def to_unsigned32(x):
    return x & 0xFFFFFFFF


def to_signed32(value):
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def format(value):
    return f"0b{to_unsigned32(value):032b}"


def decode_j_imm(instr):
    bits = instr[0] + instr[12:20] + instr[11] + instr[1:11] + "0"
    return bin_to_signed(bits)


def decode_b_imm(instr):
    bits = instr[0] + instr[24] + instr[1:7] + instr[20:24] + "0"
    return bin_to_signed(bits)


def err(line, msg):
    raise Exception(f"Line {line}: {msg}")


def is_valid_word_memory_address(addr):
    if addr % 4 != 0:
        return False
    return (STACK_START <= addr <= STACK_END) or (DATA_START <= addr <= DATA_END)


def exec_r(instr, r, line_no):
    funct7 = instr[0:7]
    rs2 = int(instr[7:12], 2)
    rs1 = int(instr[12:17], 2)
    funct3 = instr[17:20]
    rd = int(instr[20:25], 2)

    a, b = r[rs1], r[rs2]

    R = {
        ("000","0000000"): a + b,
        ("000","0100000"): a - b,
        ("111","0000000"): a & b,
        ("110","0000000"): a | b,
        ("100","0000000"): a ^ b,
        ("001","0000000"): a << (b & 0x1F),
        ("101","0000000"): to_unsigned32(a) >> (b & 0x1F),
        ("010","0000000"): int(to_signed32(a) < to_signed32(b)),
        ("011","0000000"): int(to_unsigned32(a) < to_unsigned32(b)),
    }

    if (funct3, funct7) not in R:
        err(line_no, "Unsupported R-type instruction")

    r[rd] = to_unsigned32(R[(funct3, funct7)])


def exec_i(instr, r, memory, pc, next_pc, line_no):
    op = instr[25:]
    imm = bin_to_signed(instr[0:12])
    rs1 = int(instr[12:17], 2)
    funct3 = instr[17:20]
    rd = int(instr[20:25], 2)

    if op == "0010011":
        if funct3 == "000":
            r[rd] = to_unsigned32(r[rs1] + imm)
        elif funct3 == "011":
            r[rd] = int(to_unsigned32(r[rs1]) < to_unsigned32(imm))
        else:
            err(line_no, "Unsupported I-type instruction")

    elif op == "0000011":
        if funct3 != "010":
            err(line_no, "Unsupported load instruction")

        addr = to_unsigned32(r[rs1] + imm)
        if not is_valid_word_memory_address(addr):
            print(f"Line {line_no}: Invalid memory access at 0x{addr:08X}")
            return next_pc, False

        r[rd] = to_unsigned32(memory.get(addr, 0))

    elif op == "1100111":
        if funct3 != "000":
            err(line_no, "Unsupported jalr instruction")

        temp = next_pc
        target = to_unsigned32(r[rs1] + imm)

        if target % 4 != 0:
            err(line_no, "Misaligned PC")

        next_pc = target & ~1
        r[rd] = to_unsigned32(temp)

    return next_pc, True


def exec_s(instr, r, memory, line_no):
    if instr[17:20] != "010":
        err(line_no, "Unsupported store instruction")

    imm = bin_to_signed(instr[0:7] + instr[20:25])
    rs2 = int(instr[7:12], 2)
    rs1 = int(instr[12:17], 2)

    addr = to_unsigned32(r[rs1] + imm)
    if not is_valid_word_memory_address(addr):
        print(f"Line {line_no}: Invalid memory access at 0x{addr:08X}")
        return False

    memory[addr] = to_unsigned32(r[rs2])
    return True


def exec_b(instr, r, pc, next_pc, line_no):
    imm = decode_b_imm(instr)
    rs1 = int(instr[12:17], 2)
    rs2 = int(instr[7:12], 2)
    funct3 = instr[17:20]

    a, b = r[rs1], r[rs2]

    ops = {
        "000": lambda: a == b,
        "001": lambda: a != b,
        "100": lambda: to_signed32(a) < to_signed32(b),
        "101": lambda: to_signed32(a) >= to_signed32(b),
        "110": lambda: to_unsigned32(a) < to_unsigned32(b),
        "111": lambda: to_unsigned32(a) >= to_unsigned32(b),
    }

    if funct3 not in ops:
        err(line_no, "Unsupported branch instruction")

    if ops[funct3]():
        next_pc = to_unsigned32(pc + imm)

    return next_pc


def exec_u(instr, r, pc):
    op = instr[25:]
    rd = int(instr[20:25], 2)
    imm = to_unsigned32(int(instr[0:20], 2) << 12)

    if op == "0110111":
        r[rd] = imm
    else:
        r[rd] = to_unsigned32(pc + imm)


def exec_j(instr, r, pc, next_pc):
    rd = int(instr[20:25], 2)
    imm = decode_j_imm(instr)

    r[rd] = to_unsigned32(next_pc)
    return to_unsigned32(pc + imm)


def parse(file):
    code, lines = [], []
    with open(file) as f:
        for i, l in enumerate(f, 1):
            l = l.strip()
            if not l:
                continue
            if len(l) != 32 or any(c not in "01" for c in l):
                err(i, "Invalid instruction")
            code.append(l)
            lines.append(i)

    if not code:
        err(1, "Empty file")

    if len(code) > MAX_INSTRUCTIONS:
        err(lines[MAX_INSTRUCTIONS], "Too large")

    return code, lines

# ---------------- MAIN SIM ---------------- #

def simulate(code, lines):
    r = [0] * 32
    memory = {}
    pc = 0
    steps = 0
    trace_lines = []

    r[2] = 0x17C

    while 0 <= pc < len(code) * 4:
        if steps >= MAX_STEPS:
            err(lines[min(pc // 4, len(lines)-1)], "Infinite loop")

        steps += 1

        i = pc // 4
        instr = code[i]
        line_no = lines[i]

        if instr == HALT_INSTR:
            r[0] = 0
            trace_lines.append(" ".join([format(pc)] + [format(x) for x in r]))
            return trace_lines, memory, True

        next_pc = pc + 4
        op = instr[25:]
        
        if op == "0110011":
            exec_r(instr, r, line_no)

        elif op in ("0010011", "0000011", "1100111"):
            next_pc, ok = exec_i(instr, r, memory, pc, next_pc, line_no)
            if not ok:
                r[0] = 0
                trace_lines.append(" ".join([format(pc)] + [format(x) for x in r]))
                return trace_lines, memory, False

        elif op == "0100011":
            if not exec_s(instr, r, memory, line_no):
                r[0] = 0
                trace_lines.append(" ".join([format(pc)] + [format(x) for x in r]))
                return trace_lines, memory, False

        elif op == "1100011":
            next_pc = exec_b(instr, r, pc, next_pc, line_no)

        elif op in ("0110111", "0010111"):
            exec_u(instr, r, pc)

        elif op == "1101111":
            next_pc = exec_j(instr, r, pc, next_pc)

        else:
            err(line_no, f"Unsupported opcode {op}")

        r[0] = 0
        pc = next_pc

        trace_lines.append(" ".join([format(pc)] + [format(x) for x in r]))
    err(lines[-1], "Program terminated without Virtual Halt")
    return trace_lines, memory, False

def write_outputs(trace_lines, memory, output_trace_file, include_memory_dump=True):
    with open(output_trace_file, "w") as f:
        for line in trace_lines:
            f.write(line + "\n")
        if include_memory_dump:
            for addr in range(DATA_START, DATA_END + 1, 4):
                val = memory.get(addr, 0)
                f.write(f"0x{addr:08X}:{format(val)}\n")

def main():
    if len(sys.argv) < 3:
        raise ValueError("Usage: python3 Simulator.py <input_machine_code_path> <output_trace_path>")

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    code, lines = parse(input_file)
    trace_lines, memory, completed = simulate(code, lines)
    
    write_outputs(trace_lines, memory, output_file, include_memory_dump=completed)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e))