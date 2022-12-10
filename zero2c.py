from pprint import pprint

def error(i, line):
  print("Error on line", i + 1)
  print(line)
  exit(1)


# read file

"""
lines = []
with open("assembler.zero") as file:
  for i, line in enumerate(file):
    line = line.split("#")[0]
    line = line.strip()
    if line != "":
      lines.append((i, line))
"""

TEST = """
# Fibonacci
@fib 1:1 {
  JLT .else r0 2
  RET r0
.else
  r2 = SUB r0 2
  r2 = @fib r2
  r3 = SUB r0 1
  r3 = @fib r3
  r0 = ADD r2 r3
  RET r0  
}

@start 0:0 {
  r0 = @fib 25
  DBG r0
}
"""

lines = []
for i, line in enumerate(TEST.split("\n")):
  line = line.split("#")[0]
  line = line.strip()
  if line != "":
    lines.append((i, line))

# pprint(lines)
# print("---")


# parse functions

IDEN = "abcdefghijklmnopqrstuvwxyz_"

funs = dict()
n = 0
while n < len(lines):
  try:
    i, line = lines[n]
    iden, sig, open = line.split()
    at, iden = iden[0], iden[1:]
    inr, out = map(int, sig.split(":"))

    assert at == "@"
    assert open == "{"
    for char in iden:
      assert char in IDEN
    assert iden not in funs

    block = []
    while True:
      n += 1
      i, line = lines[n]
      if line == "}": break
      block.append((i, line))

    funs[iden] = (inr, out, block)
  except:
    error(i, line)
  n += 1

# pprint(funs)
# print("---")


# Emit C code

OP = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

RUNTIME = """
// Cobbled together with love by Anima
#include <stdint.h>
#include <stdio.h>
"""

print(RUNTIME)

def generate_param(n):
  print("typedef struct {")
  for i in range(n):
    print(f"  v{i}: uint64_t,")
  print(f"}} param{n}_t;")

for i in range(0, 5):
  generate_param(i)

def declare_input_registers(n, regs):
  for i in range(n):
    print(f"  uint64_t r{i} = a.v{i};")
    regs.add(i)

def emit_label(i, iden, fun):
  for char in iden:
    assert char in IDEN
  print(f"{fun}__{iden}:  // {i}")

def wrap_t(vals):
  n = len(vals)
  nvals = []
  for i, val in enumerate(vals):
    nvals.append(f"v{i}: {val}")
  inner = ", ".join(nvals)
  return f"param{n}_t {{ {inner} }}"

def op2(op):
  def f(a, b):
    return wrap_t([f"{a} {op} {b}"])
  return f

def ret(*args):
  return f"return { wrap_t(args) }"

def jump2(op):
  def f(label, a, b):
    return f"a {op} b ? {{ goto {label}; }} : { wrap_t(['0LL']) }"
  return f

OP_simple_case = {
  "LIT": lambda a: wrap_t([f"{a}"]),

  "ADD": op2("+"),
  "SUB": op2("-"),
  "MUL": op2("*"),
  "DIV": op2("/"),
  "MOD": op2("%"),
  "SHL": op2("<<"),
  "SHR": op2(">>"),

  "EQL": op2("=="),
  "NEQ": op2("!="),
  "GTE": op2(">="),
  "LTE": op2("<="),
  "SGT": op2(">"),
  "SLT": op2("<"),

  "NOT": lambda a: wrap_t([f"!{a}"]),
  "AND": op2("&"),
  "IOR": op2("|"),
  "XOR": op2("^"),

  "GET": lambda a: wrap_t([f"mem[{a}]"]),
  "SET": lambda a, b: \
    wrap([f"{{ mem[{a}] = {b}; }}"]),

  "RET": ret,
  "JMP": lambda a: f"goto {a}",
  "JNZ": lambda a, b: jump2("!=")(a, b, "0LL"),
  "JEQ": jump2("=="),
  "JNE": jump2("!="),
  "JGE": jump2(">="),
  "JLE": jump2("<="),
  "JGT": jump2(">"),
  "JLT": jump2("<"),

  # TODO: make into an expression returning a
  "DBG": lambda a: f'printf("%d\\n", {a})',
}

def emit_line(i, line, fun, regs, out, funs):
  # print("  //", line)
  if line[0] == ".":
    emit_label(i, line[1:], fun)
    return

  results = []
  if "=" in line:
    results, instr = line.split("=")
    results = results.strip().split(" ")
  else:
    instr = line  

  op, *args = instr.strip().split(" ")
  function = False
  if op[0] == "@":
    function = True
    for char in op[1:]:
      assert char in IDEN
    op = op[1:]
  else:
    assert len(op) == 3
    for char in op:
      assert char in OP

  nargs = []
  for arg in args:
    if arg[0] == "r":
      n = int(arg[1:])
      assert n in regs
      nargs.append(f"r{n}")
    elif arg[0] == "'":
      # NOTE: does not work with space,
      # instead use decimal literal 32
      assert len(arg) == 3
      n = ord(arg[1])
      assert arg[2] == "'"
      nargs.append(f"{n}LL")
    elif arg[0] in "0123456789":
      n = int(arg)
      nargs.append(f"{n}LL")
    elif arg[0] == ".":
      for char in arg[1:]:
        assert char in IDEN
      nargs.append(f"{fun}__{arg[1:]}")
    else:
      error(i, line)
  args = nargs    

  nresults = []
  for result in results:
    assert result[0] == "r"
    n = int(result[1:])
    if n not in regs:
      print(f"  uint64_t r{n};")
    regs.add(n)
    nresults.append(n)
  results = nresults

  print("  ", end="")
  if len(results) > 0:
    n = len(results)
    print(f"param{n}_t o{i} = ", end="")
  
  if function:
    inr, out, _ = funs[op]
    assert len(args) == inr
    assert len(results) == out
    print(f"{op}({ wrap_t(args) });")
  elif op in OP_simple_case:
    expr = OP_simple_case[op](*args)
    print(f"{expr};")
  else:
    error(i, line)

  for n, result in enumerate(results):
    print(f"  r{result} = o{i}.v{n};")

for fun, (inr, out, block) in funs.items():
  regs = set()
  print()
  print(f"param{out}_t ", end="")
  print(f"{fun}(param{inr}_t a) {{")
  declare_input_registers(inr, regs)
  
  for i, line in block:
    emit_line(i, line, fun, regs, out, funs)

  print("}")

assert "start" in funs

ENTRYPOINT = """
int main() {
  start(param0_t {});
  return 0;
}
"""

print(ENTRYPOINT)
