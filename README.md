# CSE112 - Semester Project Winter 2026
**CSE112 - Computer Organisation**

**Objective:** To create a basic assembler and simulator for RISC-V ISA.

**Language**: Python

# RV32I_ISA-Assembler-Simulator
This is our semester project for **Computer Organisation (CO)** course. We have implemented a subset of the RV32I instruction set in Python, covering both an Assembler (Part 1) and a Simulator (Part 2).

# Part-1: Assembler

The assembler reads a file containing RISC-V assembly instructions, performs syntax and semantic checks, and converts them into 32-bit machine code (binary format).

## Supported Instructions
 
| Type   | Instructions                                      |
|--------|---------------------------------------------------|
| R-Type | `add`, `sub`, `and`, `or`, `slt`, `sll`, `sltu`, `xor`, `srl` |
| I-Type | `addi`, `sltiu`, `lw`, `jalr`                    |
| S-Type | `sw`                                              |
| B-Type | `beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu`        |
| U-Type | `lui`, `auipc`                                    |
| J-Type | `jal`                                             |
 
## Supported Registers
 
Both numeric and ABI register names are supported.
 
- **Numeric:** `x0` – `x31`
- **ABI:** `zero`, `ra`, `sp`, `gp`, `tp`, `t0`–`t6`, `s0`–`s11`, `a0`–`a7`, `fp`
 
## Immediate Value Constraints
 
| Type   | Bits    | Range                   |
|--------|---------|-------------------------|
| I-type | 12 bits | −2048 to 2047           |
| S-type | 12 bits | −2048 to 2047           |
| B-type | 13 bits | −4096 to 4094           |
| U-type | 20 bits | −524288 to 524287       |
| J-type | 21 bits | −1048576 to 1048574     |

# Assembler Assumptions

The assembler assumes:

-   Each instruction occupies 4 bytes.

-   The program counter (PC) starts at 0.

-   Branch offsets are relative to the current PC.

-   Branch and label offsets must be multiples of 2.

-   Labels are resolved using a two-pass approach. In the first pass, all labels and their corresponding instruction addresses are recorded. In the second pass, instructions referencing labels (such as branch and jump instructions) are encoded using the computed PC-relative offsets.

-   Labels are converted to relative PC offsets. Offset is calculated as: `offset = label_address − current_PC`

-   Labels represent instruction addresses.

-   Immediate values are given in decimal, hexadecimal, or binary.

-   Only the supported instructions listed above are used.

-   Each instruction appears on a separate line.

-   Labels must appear before the instruction they reference.

-   Comments start with `;`. Anything after `;` is ignored.

-   The assembler treats `beq zero, zero, 0` as a virtual halt instruction to signal termination. This can also be written using a self-branching label such as: `halt: beq zero, zero, halt` which produces an offset of `0` after label resolution. If any of these instructions is not present in the code, the assembler will raise an error.


# Assembler Limitations

-   Only a subset of RV32I instructions is supported.

-   No support for pseudo-instructions, floating-point instructions, etc.

-   Memory addressing supports only base + immediate format. e.g. `lw x1, 8(x2)`

# Memory Assumptions

-   Program memory size is `256` bytes, allowing `64` instructions.

-   Stack memory ranges from `0x00000100` to `0x0000017F`.

-   Stack pointer is initialized to `0x0000017C`.

-   Stack grows downwards.

-   Data memory ranges from `0x00010000` to `0x0001007F`.

-   Only the first `32` locations of data memory are used.

-   Memory bounds are assumed to be enforced by the simulator, not the assembler. The assembler simply produces machine code sequentially and assumes that the simulator will load and manage instructions within the defined memory regions.

# Running the Assembler Program

Run the assembler using:
```bash
python3 assembler.py input.asm output.txt
```

Optional readable output:
```bash
python3 assembler.py input.asm output.txt readable.txt
```

# Part 2: Simulator
 
The simulator reads a binary machine-code file (as produced by the assembler) and executes it instruction by instruction, producing an execution trace and a memory dump.
 
 ## Trace Output Format
 
After each instruction execution, one line is written to the output file:
 
```
{PC} {x0} {x1} {x2} ... {x31}
```
 
All values are in 32-bit binary with `0b` prefix, e.g. `0b00000000000000000000000000000100`.
 
After a clean Virtual Halt, data memory is appended:
 
```
0x00010000:0b00000000000000000000000000000000
0x00010004:0b00000000000000000000000000000000
...
0x0001007C:0b00000000000000000000000000000000
```
 
## Simulator Assumptions
 
- The simulator reads binary files produced by the assembler (32-character `0`/`1` lines). Empty lines are skipped.
- Maximum program size: 64 instructions (256 bytes of program memory).
- PC starts at `0x00000000`.
- Register `x0` is hardwired to `0` — any write to it is silently discarded.
- Stack pointer (`x2` / `sp`) is initialised to `0x0000017C`.
- All other registers start at `0`.
- All arithmetic is 32-bit unsigned internally; signed interpretation is applied only where the spec requires it (e.g. `slt`, `blt`, `bge`).
- Overflow in `add`, `sub`, `addi` wraps silently (ignored per spec).
- `srl` / `sll` use only the lower 5 bits of the shift amount (`rs2[4:0]`).
- JALR target has its LSB cleared (`target & ~1`) before jumping. If the resulting target is not 4-byte aligned, a `Misaligned PC` error is raised. This is because the target is ccoming from register values.
 
## Memory Model
 
| Region         | Address Range               | Size        | Locations |
|----------------|-----------------------------|-------------|-----------|
| Program memory | `0x00000000` – `0x000000FF` | 256 bytes   | 64 × 32-bit |
| Stack memory   | `0x00000100` – `0x0000017F` | 128 bytes   | 32 × 32-bit |
| Data memory    | `0x00010000` – `0x0001007F` | 128 bytes   | 32 × 32-bit |
 
- Only word-aligned (`% 4 == 0`) accesses within the stack or data regions are valid.
- An invalid load (`lw`) or store (`sw`) — unaligned address or address outside both regions — immediately terminates execution. The final register state is written to the trace; the memory dump is **omitted**.
- Data memory is initialised to `0` at startup.
 
## Simulator Error Handling
 
Errors are printed to **stdout** (not the trace file) in the format:
 
```
Line <N>: <message>
```
 
| Condition | Message |
|-----------|---------|
| Load/store to invalid or unaligned address | `Line N: Invalid memory access at 0x########` |
| PC is not 4-byte aligned after an instruction | `Line N: Misaligned PC` |
| PC jumps outside the program bounds | `Line N: PC out of bounds: 0x########` |
| Unknown opcode bits | `Line N: Unsupported opcode <bits>` |
| Unsupported encoding within a known type | `Line N: Unsupported instruction` |
| Execution step limit reached (200,000 steps) | `Line N: Infinite loop` |
| Program ends without a Virtual Halt | `Line N: Program terminated without Virtual Halt` |
| Input file contains no instructions | `Line 1: Empty file` |
| Program exceeds 64 instructions | `Line N: Program too large (exceeds 64 instructions)` |
| A line is not exactly 32 binary characters | `Line N: Invalid instruction` |

## Simulator Limitations
 
- Only the instruction subset listed in Part 1 is simulated.
- No support for interrupts, exceptions, or privileged instructions.
- Maximum execution steps: 200,000 (guards against infinite loops).
- Only `lw` (load word) and `sw` (store word) memory operations are supported.
 
## Running the Simulator
 
```bash
python3 Simulator.py input_binary.txt output_trace.txt
```
 
---
 
# Running the Full Test Suite
 
From inside the `automatedTesting/` directory:
 
```bash
# Simulator tests only
python3 src/main.py --no-asm --linux
 
# Assembler tests only
python3 src/main.py --no-sim --linux
 
# Both
python3 src/main.py --linux
```
 
---
 

# Collaborators
Abhay Puri [@abhay-gh](https://www.github.com/abhay-gh)

Krish Gupta[@Krish-Coder07](https://github.com/Krish-Coder07)

Aadi Jindal [@AadiJindal7](https://github.com/AadiJindal7)

Akhil Kumar SIngh [@akhil25055-wq](https://github.com/akhil25055-wq)
