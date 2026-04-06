import sys

STACK_START, STACK_END = 0x100, 0x17F
DATA_START, DATA_END = 0x10000, 0x1007F

MAX_INSTRUCTIONS = 64

def b2s(b):
    x=int(b, 2)
    return x-(1<<len(b)) if b[0]=="1" else x

def u32(x):
    return x & 0xFFFFFFFF

def format(value):
    return f"0b{u32(value):032b}"

def err(line, msg):
    raise Exception(f"Line {line}: {msg}")

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
    mem= {}
    pc=0
    steps=0
    out=[]
    r[2]=0x17C  # stack pointer (grows downwards)

    while 0 <= pc < len(code)*4:
        i=pc//4
        instr, ln = code[i], lines[i]
        steps+=1
        npc=pc+4

        op=instr[25:]

        if op == "0110011":  #R

        elif op in ("0010011", "0000011", "1100111"): #I


        elif op == "0100011":  #S

        elif op == "1100011":  #B

        elif op in ("0110111", "0010111"): #U

        elif op == "1101111": #J
            
        else:
            err(ln, f"Unsupported opcode {op}")
        r[0]=0
        pc=npc
        out.append(" ".join([format(pc)] + [format(x) for x in r]))


