import re
from typing import List, Any, Iterable, Mapping

import parsy

from parsy import regex, string, seq, ParseError
import operator
import random

# main classes (virtual machines)


class Machine:
    def compile(self, code: Iterable[str], substitutions: Mapping[str, str], preprocessor: 'Preprocessor'):
        raise NotImplementedError("abstract class")

    def run(self, memory: 'Memory' = None, *, debug: List[str]) -> None:
        raise NotImplementedError("abstract class")

    def get_memory(self):
        raise NotImplementedError("abstract class")


class RAM(Machine):
    def __init__(self, parser: parsy.Parser):
        self.ip = None
        self.memory = None
        self.counter = None
        self.parser = parser
        self.labels = {}
        self.r_labels = {}
        self.statements = []

    def compile(self, code: Iterable[str], substitutions: Mapping[str, str], preprocessor: 'Preprocessor'):
        i = 0
        self.counter = 0
        for line in code:
            line = line.strip()
            if line == "":
                continue
            line = preprocessor.process_line(line, substitutions)
            try:
                statement = self.parser.parse(line)
            except ParseError as e:
                raise CompilerException(f"Compile error at line {line}") from e
            if isinstance(statement, list):
                self.labels[statement[0]] = i
                self.r_labels[i] = statement[0]
                statement = statement[1]
            self.statements.append(statement)
            i += 1

    def run(self, memory: 'Memory' = None, *, debug: List[str] = None) -> None:
        debug = debug or []
        self.ip = 0
        self.memory = memory or RAMMemory()
        try:
            while True:
                ip = self.ip
                if ip >= len(self.statements):
                    raise MRuntimeException("Instruction pointer out of code range")
                v = self.statements[ip].eval(self)
                if "step" in debug:
                    label = f"{self.r_labels[ip]}: " if self.ip in self.r_labels else ""
                    print(label + str(self.statements[ip]) + (f" ({v})" if v is not None else ""))
                self.ip += 1
        except HaltException:
            print("Halt")

    def list_code(self) -> str:
        return "\n".join(str(st) for st in self.statements)

    def get_memory(self):
        return self.memory


# parser generators


def get_ram_std_parser() -> parsy.Parser:
    spaces = regex(r"\s+")
    label = regex("[A-Z_]+")
    ms = regex(r"\s*")
    number = regex("-?[0-9]+").map(int)
    dref = seq(string("["), number, string("]")).map(lambda t: RamMemoryLink(t[1]))
    reg = regex("[A-Z]").map(lambda c: RamMemoryLink(ord("A") - ord(c) - 1))
    ref = dref | reg
    uref = seq(string("["), ref, string("]")).map(lambda t: RamMemoryLink(t[1]))

    lvalue = ref | uref
    rvalue = number | ref | uref

    operator_map = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.floordiv, "%": operator.mod,
                    "&": operator.and_, "|": operator.or_, "^": operator.xor, "<<": operator.lshift,
                    ">>": operator.rshift}
    operator_re = "|".join(f"\\{op}" for op in operator_map.keys())
    condition_map = {"=": operator.eq, "<>": operator.ne,
                     "<=": operator.le, "<": operator.lt, ">=": operator.ge, ">": operator.gt}
    condition_re = "|".join(f"{op}" for op in condition_map.keys())

    st_copy = seq(lvalue, ms >> string(":="), ms >> rvalue).map(lambda t: UnaryStatement(t[0], operator.pos, t[2], "+"))
    st_neg = seq(lvalue, ms >> string(":="), ms >> string("-"), ms >> rvalue).map(
        lambda t: UnaryStatement(t[0], operator.neg, t[3], "-"))
    st_bin = seq(lvalue, ms >> string(":="), ms >> rvalue, ms >> regex(operator_re), ms >> rvalue).map(
        lambda t: BinaryStatement(t[0], operator_map[t[3]], t[2], t[4], t[3]))

    st_halt = string("halt").map(lambda _: Halt())
    st_goto = seq(string("goto"), spaces >> label).map(lambda t: Goto(t[1]))
    simple_statement = st_halt | st_goto | st_bin | st_copy | st_neg

    condition = seq(rvalue, ms >> regex(condition_re), ms >> rvalue).map(
        lambda t: CondExpression(condition_map[t[1]], t[0], t[2], t[1]))
    if_st = seq(string("if"), spaces >> condition, spaces >> string("then") >> spaces >> simple_statement).map(
        lambda t: If(t[1], t[2]))
    statement_wl = simple_statement | if_st
    label_prefix = seq(label, ms >> string(":"), ms).map(lambda t: t[0])

    statement = statement_wl | seq(label_prefix, statement_wl)
    return statement


def get_ram_extended_parser() -> parsy.Parser:
    ms = regex(r"\s*")
    number = regex("-?[0-9]+").map(int)
    statement = get_ram_std_parser()
    init = seq(string("$init"), ms >> string("[") >> number, string("]"),
               ms >> regex(r"[^,]+").at_least(1).concat().sep_by(string(","))).map(lambda t: Initializer(t[1], t[3]))
    printer = (string("$print") >> ms >> regex(r"[^,]+").at_least(1).concat().sep_by(string(","))).map(
        lambda t: Printer(t))
    return statement | init | printer


# representations of virtual machine memory (including address getter/setter)


class Memory:
    """
    abstract class for virtual memories
    """
    def __getitem__(self, addr: int) -> Any:
        raise NotImplementedError("abstract class")

    def __setitem__(self, addr: int, value: Any) -> None:
        raise NotImplementedError("abstract class")

    def __contains__(self, data: Any) -> bool:
        raise NotImplementedError("abstract class")

    def get_min_address(self) -> int:
        raise NotImplementedError("abstract class")

    def get_max_address(self) -> int:
        raise NotImplementedError("abstract class")

    def list_block(self, addr_range: Iterable[int]) -> str:
        raise NotImplementedError("abstract class")

    def addr_formatter(self, addr: int) -> str:
        raise NotImplementedError("abstract class")


class RAMMemory(dict, Memory):
    def get_min_address(self) -> int:
        return min(self.keys())

    def get_max_address(self) -> int:
        return max(self.keys())

    def list_block(self, addr_range: Iterable[int]):
        return ", ".join(f"{self.addr_formatter(a)}: {self[a]}" for a in addr_range if a in self)

    def addr_formatter(self, addr: int) -> str:
        if -26 <= addr <= -1:
            return chr(ord('A') - addr - 1)
        else:
            return str(addr)


class MemoryLink:
    def get(self, memory: Memory) -> int:
        raise NotImplementedError("abstract class")

    def set(self, memory: Memory, value: int) -> None:
        raise NotImplementedError("abstract class")


class RamMemoryLink(MemoryLink):
    def __init__(self, addr):
        self.link = addr

    def get(self, memory: Memory) -> int:
        if isinstance(self.link, int):
            index = self.link
        else:
            index = self.link.get(memory)
        if index not in memory:
            raise MRuntimeException(f"Invalid (uninitialized) memory cell {memory.addr_formatter(index)}")
        return memory[index]

    def set(self, memory: Memory, value: int) -> None:
        if isinstance(self.link, int):
            memory[self.link] = value
        else:
            memory[self.link.get(memory)] = value

    def __str__(self):
        if isinstance(self.link, int) and -26 <= self.link <= -1:
            return chr(ord('A') - self.link - 1)
        return f"[{self.link}]"

# exception classes


class HaltException(Exception):
    def __init__(self):
        pass


class CompilerException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class MRuntimeException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


# representation of RAM statements (executors)

class Executor:
    def eval(self, ram: Machine):
        raise NotImplementedError("abstract class")


class BinaryStatement(Executor):
    def __init__(self, target, operation, operand1, operand2, symbol):
        self.target = target
        self.operation = operation
        self.operand1 = operand1
        self.operand2 = operand2
        self.symbol = symbol

    def __str__(self):
        return f"{self.target} <- {self.operand1} {self.symbol} {self.operand2}"

    def eval(self, ram: RAM):
        ram.counter += 1
        mem = ram.memory
        op1 = self.operand1 if isinstance(self.operand1, int) else self.operand1.get(mem)
        op2 = self.operand2 if isinstance(self.operand2, int) else self.operand2.get(mem)
        rv = self.operation(op1, op2)
        self.target.set(mem, rv)
        return rv


class UnaryStatement(Executor):
    def __init__(self, target, operation, operand1, symbol):
        self.target = target
        self.operation = operation
        self.operand1 = operand1
        self.symbol = symbol

    def __str__(self):
        return f"{self.target} <- {self.symbol if self.symbol == '-' else ''}{self.operand1}"

    def eval(self, ram: RAM):
        ram.counter += 1
        mem = ram.memory
        op1 = self.operand1 if isinstance(self.operand1, int) else self.operand1.get(mem)
        rv = self.operation(op1)
        self.target.set(mem, rv)
        return rv


class CondExpression(Executor):
    def __init__(self, operation, operand1, operand2, symbol):
        self.operation = operation
        self.operand1 = operand1
        self.operand2 = operand2
        self.symbol = symbol

    def __str__(self):
        return f"{self.operand1} {self.symbol} {self.operand2}"

    def eval(self, ram: RAM):
        ram.counter += 1
        mem = ram.memory
        op1 = self.operand1 if isinstance(self.operand1, int) else self.operand1.get(mem)
        op2 = self.operand2 if isinstance(self.operand2, int) else self.operand2.get(mem)
        return self.operation(op1, op2)


class Halt(Executor):
    def __str__(self):
        return "HALT"

    def eval(self, ram: RAM):
        raise HaltException()


class Goto(Executor):
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f"GOTO {self.label}"

    def eval(self, ram: RAM):
        ram.counter += 1
        ram.ip = ram.labels[self.label] - 1


class If(Executor):
    def __init__(self, condition, statement):
        self.condition = condition
        self.statement = statement

    def __str__(self):
        return f"IF {self.condition} THEN {self.statement}"

    def eval(self, ram: RAM):
        cvalue = self.condition.eval(ram)
        if cvalue:
            self.statement.eval(ram)
        return cvalue


# extended executors

def compact_item_iter(items):  # iterator over structured list
    for v, n in items:
        if n is None:
            n = 1
        if n > 1 and isinstance(v, Iterable):
            v = list(v)  # iterator would be exhausted after the first repeat
        for i in range(n):
            if callable(v):
                yield v()
            elif isinstance(v, Iterable):
                for sub_iter in v:
                    yield sub_iter
            else:
                yield v


def range3(a, b, s):
    """
    wrapper for standard Range
    """
    return range(a, b, 1 if s is None else s)


def rand_gen(a, b, s):
    """
    wrapper for random.randrange
    """
    return lambda: random.randrange(a, b, 1 if s is None else s)


class Initializer(Executor):
    """
    memory initializer - initializator for memories with integer addresses

    usage: '$init' '['start-address']' value-specifier['*'repeat] [',' value-specifier['*'repeat]]*
    start-address:: RE: -?[0-9]+
    repeat:: RE: [0-9]+
    value-specifier: int_literal | range | random_value | fixed_random_value
    int_literal:: RE: -?[0-9]+
    range:: int_literal ':' int_literal [':' int_literal]  = values from range (Python semantics)
    random_value :: '@' range = random value from range (in repeat every value is new random)
    fixed_random_value ::  '@@' random value from range (fixed random value is repeated)
    """
    def __init__(self, start, values):
        self.start = start
        self.values = [Initializer.item(v) for v in values]

    def eval(self, ram):
        for i, v in enumerate(compact_item_iter(self.values)):
            ram.get_memory()[self.start + i] = v

    def __str__(self):
        return f"$init [{self.start}]"

    @staticmethod
    def item(s: str):
        number = regex("-?[0-9]+").map(int)
        scalar = regex("-?[0-9]+").map(lambda x: int(x))
        range = seq(number, string(":") >> number, (string(":") >> number).optional()).map(lambda t: range3(*t))
        randval = seq(string("@") >> number, string(":") >> number, (string(":") >> number).optional()).map(
            lambda t: rand_gen(*t))
        fixrandval = seq(string("@@") >> number, string(":") >> number, (string(":") >> number).optional()).map(
            lambda t: rand_gen(*t)())
        item_parser = seq(fixrandval | randval | range | scalar, (string("*") >> number).optional())
        return item_parser.parse(s)


class Printer(Executor):
    """
        print memory contents

        usage: '$print' addr-spec [ ',' addr-spec]*
        addr-spec :: address | range
        address :: RE: -?[0-9]+
        range :: address ':' address [':' address]
    """
    def __init__(self, ranges):
        self.ranges = [Printer.range(v) for v in ranges]

    @staticmethod
    def range(s: str):
        address = regex("-?[0-9]+").map(int)
        prange = seq(address, string(":") >> address, (string(":") >> address).optional()).map(lambda t: range3(*t))
        return prange.parse(s)

    def eval(self, ram):
        for r in self.ranges:
            print(ram.get_memory().list_block(r))

    def __str__(self):
        return "$print"

# preprocessor


class Preprocessor:
    def process_line(self, line: str, substitutions: Mapping[str, str]) -> str:
        raise NotImplementedError("abstract class")


class StdPreprocessor(Preprocessor):
    def __init__(self, end_line_comment: str = None, strip: bool = True):
        self.elc = end_line_comment
        self.strip = strip

    def process_line(self, line: str, substitutions: Mapping[str, str]) -> str:
        for sid, sub in substitutions.items():
            line = line.replace(f"{{{sid}}}", sub)
        if "{" in line or "}" in line:
            raise CompilerException(f"Unsubstituted text in `{line}`")
        if self.elc is not None:
            pattern = "\\" + self.elc + ".*$"
            line = re.sub(pattern, "", line)
        if self.strip:
            line = line.strip()
        return line
