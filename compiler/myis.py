registers = ["eax", "ebx", "ecx", "edx", "esp", "ebp", "esi", "edi"]

instructions = {
    "push" : [{"opcode" : 0x00, "format" : "<cc",  "params" : ["reg"]}],
    "pop"  : [{"opcode" : 0x01, "format" : "<cc",  "params" : ["reg"]}],
    "mov"  : [{"opcode" : 0x02, "format" : "<ccI", "params" : ["reg", "imm"]},
              {"opcode" : 0x03, "format" : "<ccc", "params" : ["reg", "reg"]},
              {"opcode" : 0x04, "format" : "<ccc", "params" : ["reg", "@reg"]},
              {"opcode" : 0x05, "format" : "<ccc", "params" : ["@reg", "reg"]},
              {"opcode" : 0x06, "format" : "<ccI", "params" : ["reg", "ref"]}
             ],
    "inc"  : [{"opcode" : 0x07, "format" : "<cc",  "params" : ["reg"]}],
    "dec"  : [{"opcode" : 0x08, "format" : "<cc",  "params" : ["reg"]}],
    "add"  : [{"opcode" : 0x09, "format" : "<ccc", "params" : ["reg", "reg"]}],
    "jmp"  : [{"opcode" : 0x0A, "format" : "<cI",  "params" : ["ref"]}],
    "jz"   : [{"opcode" : 0x0B, "format" : "<ccI", "params" : ["reg", "ref"]}],
    "jnz"  : [{"opcode" : 0x0C, "format" : "<ccI", "params" : ["reg", "ref"]}],
    "mul"  : [{"opcode" : 0x0D, "format" : "<ccc", "params" : ["reg", "reg"]}],
    "halt" : [{"opcode" : 0xFF, "format" : "<c",   "params" : []}],
    "emit" : [{"opcode" : None, "format" : "<s",   "params" : ["str"]}]
}
