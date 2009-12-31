# Tadas Vilkeliskis <vilkeliskis.t@gmail.com>, 2009
import io
import sys
import struct
import re

class Compiler(object):
    def __init__(self, itable, registers, verbose):
        self.__itable = itable
        self.__registers = registers
        self.__tokens = list()
        self.__program = ""
        self.__programLen = 0
        self.__symbolTable = dict()
        self.__referenceTable = list()
        self.__verbose = verbose

    # Return the bytecode of a program.
    def getProgram(self):
        return self.__program

    # Return the length of a program.
    def getProgramLen(self):
        return self.__programLen

    # Identifies and returns the next token from the token list.
    def __nextToken(self):
        token = ("", "")
        if (len(self.__tokens) > 0):
            t = self.__tokens.pop(0)
            if t in self.__itable:
                token = ("instr", t);
            elif t in self.__registers:
                token = ("reg", t)
            elif t[0] == "@":
                token = ("@reg", t)
            elif re.match('^str\((.*?)\)', t) != None:
                token = ("str", eval(t))
            elif re.match('^int\((.*?)\)', t) != None:
                token = ("imm", eval(t))
            elif t[len(t)-1] == ":":
                token = ("lab", t[:len(t)-1])
            elif t.isalnum():
                token = ("ref", t)
        return token

    # Appends bytecode to the program of the given instruction.
    def __doInstruction(self, instructionName):
        result = False
        # In some cases an instruction can have different types of arguments
        # (list in instruction table). So, we go through each of them.
        for instruction in self.__itable[instructionName]:
            tokenBackup = []
            params = []
            # Pull as many tokens as parameters the instruction take.
            for p in instruction["params"]:
                tmp = self.__nextToken()
                tokenBackup.append(tmp)
                params.append(tmp[0])
            # Push all tokens back to the token list if current parameter list
            # does not match instruction's.
            if instruction["params"] != params:
                while len(tokenBackup) > 0:
                    tmp = tokenBackup.pop()
                    self.__tokens.insert(0, tmp[1])
                continue
            # We found the instruction in the instruction table. The
            # compilation begins.
            
            # Have to take a copy of the format because we may overwrite when
            # string is encountered
            format = instruction["format"]

            if instruction["opcode"] != None:
                instructionCode = [chr(instruction["opcode"])]
            else:
                instructionCode = []
            for t in tokenBackup:
                if t[0] == "reg":
                    # For registers we take their position in the registers
                    # table.
                    instructionCode.append(chr(self.__registers.index(t[1])))
                elif t[0] == "@reg":
                    instructionCode.append(chr(self.__registers.index(t[1][1:])))
                elif t[0] == "imm":
                    # Nothing special for immediate values.
                    instructionCode.append(t[1])
                elif t[0] == "str":
                    length = len(t[1])
                    try:
                        index = format.index("s")
                    except ValueError:
                        print "Wrong instruction format: 's' missing. Skipping"
                        return

                    format = format[:index] + 's' * length + format[index + 1:]
                    for c in t[1]:
                        instructionCode.append(c)
                elif t[0] == "ref":
                    # If it's a reference we add it to the reference table.
                    # Additionally, we calculate the location of the reference
                    # and where the current instruction begins in the code.
                    l = len(instructionCode)
                    f = format[:l+1]
                    address = self.__programLen + len(struct.pack(f,
                                                            *instructionCode))
                    # A reference address placeholder.
                    instructionCode.append(0)
                    self.__doReference(t[1], self.__programLen, address)
            if self.__verbose == True:
                print "%08X: %08X %08s: " % (self.__programLen,
                                             len(instructionCode),
                                             instructionName),
                print instructionCode
            # Convert everything to binary
            packed = struct.pack(format, *instructionCode)
            self.__programLen += len(packed)
            self.__program += packed
            result = True
            break
        return result

    # Adds a label to the symbol table
    def __doLabel(self, label):
        self.__symbolTable[label] = self.__programLen

    # Adds a reference to the reference table
    def __doReference(self, name, instrstart, address):
        self.__referenceTable.append({"name"       : name,
                                      "instrstart" : instrstart,
                                      "address"    : address})

    # Tokenizes a given file
    def parseFile(self, filename):
        file = io.open(filename, "r")
        s = file.read();
        file.close()
        s = s.strip()
        sep = re.compile("[\s\n]+")
        self.__tokens = sep.split(s)

    # Performs the compilation
    def compile(self):
        while len(self.__tokens) > 0:
            token = self.__nextToken()
            if token[0] == "instr":
                result = self.__doInstruction(token[1])
            elif token[0] == "lab":
                result = self.__doLabel(token[1])
            else:
                print "Not a label/instruction: " + token[1] + ". Skipping."
                continue

            if result == False:
                print "Not in the instruction set: " + token[1] + ". Skipping."

    # Links labels and their references
    def link(self):
        if self.__verbose == True:
            print "\nInformation from linking stage:"
        for r in self.__referenceTable:
            try:
                labelpos = self.__symbolTable[r["name"]]
                offset = labelpos - r["instrstart"]
                address = struct.pack("<I", offset)
                x = r["address"]
                self.__program = (self.__program[:x] + 
                                  address + self.__program[x+4:])

                if self.__verbose == True:
                    s = ""
                    for c in address:
                        c = hex(ord(c))[2:]
                        if len(c) != 2:
                            c = "0" + c
                        s += c
                    print "%08X -> %s (%s)" % (x, s, r["name"])

            except KeyError:
                print "Unresolved reference: " + r["name"]

    # Self-explanatory
    def dump(self):
        print "Symbol table:"
        print self.__symbolTable
        print "Reference table:"
        print self.__referenceTable
        print "Bytecode:"
        print map(hex, map(ord, self.__program))

