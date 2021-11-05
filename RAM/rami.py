#!/bin/env python

import argparse
from machines import RAM, get_ram_extended_parser, StdPreprocessor

parser = argparse.ArgumentParser(description='RAM (Random Access Machine) interpreter')
parser.add_argument("-d", "--debug", help="set debug option", action='append', choices=['step'])
parser.add_argument("-c", help="print instruction count", action='store_true')
parser.add_argument("-s", "--substitute", help="substitution", action='append')
parser.add_argument("filename", help="file with instructions for RAM")

arg = parser.parse_args()

subdict = {}
if arg.substitute:
    subs = ",".join(arg.substitute)
    for s in subs.split(","):
        k, v = s.split("=")
        subdict[k]=v

file = open(arg.filename, "rt")
ram = RAM(get_ram_extended_parser())
ram.compile(code=file, substitutions=subdict, preprocessor=StdPreprocessor(end_line_comment="#"))
ram.run(debug=(arg.debug or []))
if arg.c:
    print(f"Instruction count: {ram.counter}")
