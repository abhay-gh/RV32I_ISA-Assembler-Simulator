import sys

Register_Map = {
  "zero": "00000", "x0": "00000", "x1": "00001", "x2": "00010", "x3": "00011", "x4": "00100", "x5": "00101",
  "x6": "00110", "x7": "00111", "x8": "01000", "x9": "01001", "x10": "01010", "x11": "01011", "x12": "01100",
  "x13": "01101", "x14": "01110",  "x15": "01111", "x16": "10000",  "x17": "10001", "x18": "10010",
  "x19": "10011", "x20": "10100", "x21": "10101", "x22": "10110", "x23": "10111", "x24": "11000", "x25": "11001",
  "x26":  "11010", "x27":  "11011", "x28": "11100", "x29": "11101", "x30": "11110", "x31": "11111",
  "ra": "00001",  "sp": "00010", "gp": "00011",  "tp": "00100", 
  "t0": "00101",  "t1": "00110", "t2": "00111", "t3": "11100",   "t4": "11101", "t5": "11110", "t6": "11111",
  "s0": "01000", "fp": "01000", "s1": "01001",  "s2": "10010", "s3": "10011", "s4": "10100", "s5": "10101",
  "s6": "10110", "s7": "10111", "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011", 
  "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110", "a5": "01111","a6": "10000", 
  "a7": "10001"
}

R_type_Opcode = "0110011"

R_type_funct7_funct3 = {
    "add": {"funct7": "0000000", "funct3": "000"},
    "sub": {"funct7": "0100000", "funct3": "000"},
    "and": {"funct7": "0000000", "funct3": "111"},
    "or":  {"funct7": "0000000", "funct3": "110"},
    "slt": {"funct7": "0000000", "funct3": "010"},
    "sll": {"funct7": "0000000", "funct3": "001"},
    "sltu":{"funct7": "0000000", "funct3": "011"},
    "xor": {"funct7": "0000000", "funct3": "100"},
    "srl": {"funct7": "0000000", "funct3": "101"}
}

I_type = {
    "addi": {"opcode": "0010011", "funct3": "000"},
    "sltiu":{"opcode": "0010011", "funct3": "011"},
    "lw":   {"opcode": "0000011", "funct3": "010"},
    "jalr": {"opcode": "1100111", "funct3": "000"}
}

S_opcode = "0100011"

S_funct3 = {
    "sw": "010"
}

B_opcode = "1100011"

B_funct3 = {
    "beq": "000",
    "bne": "001",
    "blt": "100",
    "bge": "101",
    "bltu":"110",
    "bgeu":"111"
}

U_type = {
    "lui": "0110111",
    "auipc": "0010111"
}

J_opcode = "1101111"

def decimal_to_signed_binary(value, bits):
    if value < 0:
        value = (1 << bits) + value
    binary_string = format(value, "b")
    padding_length = bits - len(binary_string)
    if padding_length > 0:
        binary_string = "0" * padding_length+binary_string
    
    return binary_string

def check_reg(r, line_no):
    if r not in Register_Map:
        raise ValueError("Line " + str(line_no) + ": Invalid register " + r)
      
def check_operands(parts, expected, line_no):
    if len(parts) < expected:
        raise ValueError("Line " + str(line_no) + ": Too few operands for " + parts[0])
    if len(parts) > expected:
        raise ValueError("Line " + str(line_no) + ": Too many operands for " + parts[0])
def parse_immediate(imm_str, line_no):
    try:
        return int(imm_str, 0)
    except ValueError:
        raise ValueError("Line " + str(line_no) + ": Invalid immediate value '" + imm_str + "'")
def check_range(val, bits, line_no):
    limit = 1 << (bits - 1)
    minimum = -limit
    maximum = limit - 1
    if val < minimum or val > maximum:
        raise ValueError("Line " + str(line_no) + ": Immediate out of range")

def first_pass(lines):
    labels = {}
    pc = 0
    for idx, line in enumerate(lines):
        line = line.split(";")[0].strip()
        if not line:
            continue
        if ":" in line:
            raw_before_colon = line.split(":")[0]
            label_text = raw_before_colon.lstrip()
            if label_text != label_text.rstrip():
                raise ValueError("Line " + str(idx+1) + ": No space allowed between label and colon")
            label = label_text.strip()
            if not label:
                raise ValueError("Line " + str(idx+1) + ": Empty label")
            if not label[0].isalpha():
                raise ValueError("Line " + str(idx+1) + ": Label must start with a letter")
            if label in labels:
                raise ValueError("Line " + str(idx+1) + ": Duplicate label '" + label + "'")
            labels[label] = pc
            if line.split(":")[1].strip():
                pc += 4
        else:
            pc += 4
    return labels

def assemble(lines):
  
  labels = first_pass(lines)
  pc = 0
  output = []
  halt_line = -1
  last_instruction_line = -1
  
  for i in range(len(lines)):
    line_no = i+1
    line = lines[i].split(";")[0].strip()
    
    if not line :
      continue
      
    if ":" in line :
      line = line.split(":")[1].strip()
      if not line :
        continue
        
    formatted_line = line.replace(","," ")
    formatted_line = formatted_line.replace("("," ")
    formatted_line = formatted_line.replace(")", " ")
    parts = formatted_line.split()
    opcode = parts[0]
    last_instruction_line = line_no
    
    if opcode in R_type_funct7_funct3 :
        check_commas(line, 2, line_no)
        check_operands(parts, 4, line_no)
        rd = parts[1]
        rs1 = parts[2]
        rs2 = parts[3]
        check_reg(rd,line_no)
        check_reg(rs1,line_no)
        check_reg(rs2,line_no)
        funct7 = R_type_funct7_funct3[opcode]["funct7"]
        funct3 = R_type_funct7_funct3[opcode]["funct3"]
        binary_code = (funct7 + Register_Map[rs2] + Register_Map[rs1] + funct3 + Register_Map[rd] + R_type_Opcode)
    
    elif opcode in I_type :
        if opcode == "lw":
            check_commas(line, 1, line_no)
        elif opcode == "jalr" and "(" in line and ")" in line:
            check_commas(line, 1, line_no)
        else:
            check_commas(line, 2, line_no)
        check_operands(parts, 4, line_no)
        if opcode == "lw" or (opcode == "jalr" and "(" in line and ")" in line):
            rd = parts[1]
            imm = parts[2]
            rs1 = parts[3]
        else :
            rd = parts[1]
            rs1 = parts[2]
            imm = parts[3]
        check_reg(rd,line_no)
        check_reg(rs1,line_no)
        imm_val = parse_immediate(imm, line_no)
        check_range(imm_val,12,line_no)
        imm_binary = decimal_to_signed_binary(imm_val, 12)
        binary_code = (imm_binary + Register_Map[rs1] + I_type[opcode]["funct3"] + Register_Map[rd] + I_type[opcode]["opcode"])
    
    elif opcode in S_funct3:
        rs2 = parts[1]
        imm = parts[2]
        rs1 = parts[3]
        check_reg(rs1,line_no)
        check_reg(rs2,line_no)
        imm_val = int(imm, 0)
        check_range(imm_val,12,line_no)
        imm_binary = decimal_to_signed_binary(imm_val, 12)
        upper = imm_binary[:7]
        lower = imm_binary[7:]
        binary_code = upper + Register_Map[rs2] + Register_Map[rs1] + S_funct3[opcode] + lower + S_opcode
    
    elif opcode in B_funct3:
        rs1 = parts[1]
        rs2 = parts[2]
        target = parts[3]
        check_reg(rs1,line_no)
        check_reg(rs2,line_no)
        if target in labels:
            offset = labels[target] - pc
        else:
            offset = int(target,0)
        check_range(offset,13,line_no)
        imm_binary = decimal_to_signed_binary(offset, 13)
        imm = imm_binary[:-1]
        imm_12   = imm[0]
        imm_10_5 = imm[2:8]
        imm_4_1  = imm[8:12]
        imm_11   = imm[1]
        binary_code = imm_12 + imm_10_5 + Register_Map[rs2] + Register_Map[rs1] + B_funct3[opcode] + imm_4_1 + imm_11 + B_opcode
        if opcode == "beq" and Register_Map[rs1] == "00000" and Register_Map[rs2] == "00000" and offset == 0:
            halt_line = line_no
    
    elif opcode in U_type:
        rd = parts[1]
        imm = parts[2]
        check_reg(rd,line_no)
        imm_val = int(imm, 0)
        check_range(imm_val,20,line_no)
        imm_binary = decimal_to_signed_binary(imm_val, 20)
        binary_code = imm_binary + Register_Map[rd] + U_type[opcode]
    
    elif opcode == "jal":
        rd = parts[1]
        target = parts[2]
        check_reg(rd,line_no)
        if target in labels:
            offset = labels[target] - pc
        else:
            offset = int(target, 0)
        check_range(offset,21,line_no)
        imm_binary = decimal_to_signed_binary(offset, 21)
        imm = imm_binary[:-1]
        imm_20    = imm[0]
        imm_10_1  = imm[10:20]
        imm_11    = imm[9]
        imm_19_12 = imm[1:9]
        binary_code = imm_20 + imm_10_1 + imm_11 + imm_19_12 + Register_Map[rd] + J_opcode
    
    else:
        raise ValueError("Line " + str(line_no) + ": Unknown instruction " + opcode)
    
    output.append(binary_code)
    pc = pc+4
  
  if halt_line == -1:
      raise ValueError("Virtual halt missing (beq zero,zero,0)")
  if halt_line != last_instruction_line:
      raise ValueError("Virtual halt must be last instruction")
  return output
