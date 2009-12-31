#!/usr/bin/python -W ignore::DeprecationWarning

import compiler
import myis
import sys
import getopt
import io

def usage(): 
    print "Mini Compiler for Virtual Machines v1.0"
    print "Tadas Vilkeliskis <vilkeliskis.t@gmail.com>, 2009"
    print
    print "Usage: " + sys.argv[0] + " [-v] -o <out file> -s <style> <source file>"
    print "     -v  Verbose mode."
    print "     -o  Output file."
    print "     -s  Output style:"
    print "         c - Outputs a C style array."
    print "         hex - Hexadecimal representation of the code."
    print "         bin - Raw bytes."
    sys.exit(-1)
    
def writeCode(filename, program, style):
    if style == "c":
        output = u"unsigned char bytecode[] = {\n\t"
        l = len(program)
        for i in range(0, l):
            if i % 8 == 0 and i != 0:
                output += "\n\t"
            s = "'\\x%02X'" % ord(program[i])
            if i != l - 1:
                s += ", "
            else:
                s += " "
            output += s
        output += "\n};\n"
        output += "unsigned int bytecode_len = " + str(len(program)) + ";"
        f = io.open(filename, "w")
        f.write(output)
        f.close()
    elif style == "hex":
        output = u""
        for i in range(0, len(program)):
            if i % 16 == 0 and i != 0:
                output += "\n"
            output += "%02X " % ord(program[i])
        f = io.open(filename, "w")
        f.write(output)
        f.close()
    else:
        f = io.open(filename, "wb")
        f.write(program)
        f.close()


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "vo:s:")
    except getopt.GetoptError, err:
        print str(err)
        usage()

    output = None
    input = None
    style = None
    verbose = False

    for o, a in opts:
        if o == "-v":
            verbose = True
        if o == "-o":
            output = a
        if o == "-s":
            if a in ["c", "hex", "bin"]:
                style = a

    if output == None:
        print "Output file not specified."
        usage()
    if style == None:
        print "Output style not specified."
        usage()
    if len(args) == 0:
        print "Source file not specified."
        usage()
    input = args[0]

    c = compiler.Compiler(myis.instructions, myis.registers, verbose)
    c.parseFile(input)
    c.compile()
    c.link()

    program = c.getProgram()
    writeCode(output, program, style)

if __name__ == "__main__":
    main()
