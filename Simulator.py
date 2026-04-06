import sys

STACK_START, STACK_END = 0x100, 0x17F
DATA_START, DATA_END = 0x10000, 0x1007F

MAX_INSTRUCTIONS = 64

def bin_to_signed(b):
    x=int(b, 2)
    return x-(1<<len(b)) if b[0]=="1" else x

def to_unsigned32(x):
    return x & 0xFFFFFFFF

def to_signed32(value):
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value

def format(value):
    return f"0b{to_unsigned32(value):032b}"

def err(line, msg):
    raise Exception(f"Line {line}: {msg}")

def is_valid_word_memory_address(addr):
    if addr % 4 != 0:
        return False
    in_stack = STACK_START <= addr <= STACK_END
    in_data  = DATA_START <= addr <= DATA_END
    return in_stack or in_data

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

def simulate(code, lines):
    r=[0]*32
    memory= {}
    pc=0
    steps=0
    trace_lines=[]
    r[2]=0x17C  # stack pointer (grows downwards)

    while 0 <= pc < len(code)*4:
        i=pc//4
        instr, line_no = code[i], lines[i]
        steps+=1
        next_pc=pc+4

        op=instr[25:]

        if op == "0110011":  
            funct7 = instr[0:7]
            rs2, rs1, funct3, rd = int(instr[7:12],2), int(instr[12:17],2), instr[17:20], int(instr[20:25],2)
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
                raise err(line_no, "Unsupported R-type instruction")
            r[rd] = to_unsigned32(R[(funct3, funct7)])

        elif op in ("0010011", "0000011", "1100111"): 
            imm = bin_to_signed(instr[0:12])
            rs1, funct3, rd = int(instr[12:17],2), instr[17:20], int(instr[20:25],2)

            if op == "0010011": 
                if funct3 == "000":
                    r[rd] = to_unsigned32(r[rs1] + imm)
                elif funct3 == "011":
                    r[rd] = int(to_unsigned32(r[rs1]) < to_unsigned32(imm))
                else:
                    raise err(line_no, "Unsupported I-type instruction")

            elif op == "0000011":
                if funct3 != "010":
                    raise err(line_no, "Unsupported load instruction")
                addr = to_unsigned32(r[rs1] + imm)
                if not is_valid_word_memory_address(addr):
                    print(f"Line {line_no}: Invalid memory access at 0x{addr:08X}")
                    return trace_lines, memory, False
                if addr in memory:
                    r[rd] = memory[addr]
                else:
                    r[rd] = 0

            elif op == "1100111": 
                if funct3 != "000":
                    raise err(line_no, "Unsupported jalr instruction")
                temp     = next_pc
                next_pc  = to_unsigned32(r[rs1] + imm) & ~1
                r[rd] = to_unsigned32(temp)

        elif op == "0100011":  #S

        elif op == "1100011":  #B

        elif op in ("0110111", "0010111"): #U

        elif op == "1101111": #J
            
        else:
            err(line_no, f"Unsupported opcode {op}")
        r[0]=0
        pc=next_pc
        trace_lines.append(" ".join([format(pc)] + [format(x) for x in r]))


