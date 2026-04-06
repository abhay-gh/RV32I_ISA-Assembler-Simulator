import sys

STACK_START, STACK_END = 0x100, 0x17F
DATA_START, DATA_END = 0x10000, 0x1007F

MAX_INSTRUCTIONS = 64

def b2s(b):
    x=int(b, 2)
    return x-(1<<len(b)) if b[0]=="1" else x


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

