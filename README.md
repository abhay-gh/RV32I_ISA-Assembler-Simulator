# CSE112 - Semester Project Winter 2026
CSE112 - Computer Organisation

Objective: To create a basic assembler and simulator for RISC-V ISA.

Language: Python

# RV32I_ISA-Assembler-Simulator
This is our semester project for Computer Organisation (CO) course. Here, we will be implementing a subset of RV32I Instruction set using python. We will be implementing Assembler and Simulator for the listed instructions.

# Part-1: Assembler

The assembler reads a file containing RISC-V assembly instructions, performs syntax and semantic checks, and converts them into 32-bit machine code (binary format).

# Supported Instructions

-   R-Type: add, sub, and, or, slt, sll, sltu, xor, srl
-   I-Type: addi, sltiu, lw, jalr
-   S-Type: sw
-   B-Type: beq, bne, blt, bge, bltu, bgeu
-   U-Type: lui, auipc
-   J-Type: jal

# Supported Registers

Both numeric and ABI register names are supported.

Numeric Registers: x0 – x31

ABI Registers: zero, ra, sp, gp, tp, t0 – t6, s0 – s11, a0 – a7, fp

# Immediate Value Constraints

Immediate values must fit within the instruction format.

| Type   | Bits    | Range               |
| ------ | ------- | ------------------- |
| I-type | 12 bits | −2048 to 2047       |
| S-type | 12 bits | −2048 to 2047       |
| B-type | 13 bits | −4096 to 4094       |
| U-type | 20 bits | −524288 to 524287   |
| J-type | 21 bits | −1048576 to 1048574 |   

# Assumptions

The assembler assumes:

-   Each instruction occupies 4 bytes.

-   The program counter (PC) starts at 0.

-   Branch offsets are relative to the current PC.

-   Branch and label offsets must be multiples of 2.

-   Labels are converted to relative PC offsets. Offset is calculated as: offset = label_address − current_PC

-   Labels represent instruction addresses.

-   Immediate values are given in decimal, hexadecimal, or binary.

-   Only the supported instructions listed above are used.

-   Each instruction appears on a separate line.

-   Labels must appear before the instruction they reference.

-   Comments start with ';'. Anything after ';' is ignored.

-   The assembler treats 'beq zero, zero, 0' as a virtual halt instruction. This can also be written using a self-branching label such as: 'halt: beq zero, zero, halt' which produces an offset of 0 after label resolution. If any of these instructions is not present at the end, the assembler will raise an error.


# Limitations

-   Only a subset of RV32I instructions is supported.

-   No support for pseudo-instructions, floating-point instructions, etc.

-   Memory addressing supports only base + immediate format. e.g. lw x1, 8(x2)

# Running the Program

Run the assembler using:
```bash
python3 assembler.py input.asm output.txt
```

Optional readable output:
```bash
python3 assembler.py input.asm output.txt readable.txt
```

# Collaborators
Abhay Puri [@abhay-gh](https://www.github.com/abhay-gh)

Krish Gupta[@Krish-Coder07](https://github.com/Krish-Coder07)

Aadi Jindal [@AadiJindal7](https://github.com/AadiJindal7)

Akhil Kumar SIngh [@akhil25055-wq](https://github.com/akhil25055-wq)
