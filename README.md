# Language Zero

... is an assembly-like language and runtime.

Here is an example:

```rust
fn fib 1:1
  r1 = LTN r0 2
  JNZ r1 else
  RET r0
else:
  r2 = SUB r0 1
  r3 = SUB r0 2
  r2 = RUN fib r2
  r3 = RUN fib r3
  r4 = ADD r2 r3
  RET r4 
end

fn main 0:0
  r0 = fib 40
  OUT r0
end
```

This listing computes and displays the 
40th Fibonacci number.

A Language Zero module is a list of functions:

```Rust
fn NAME INPUTS:OUTPUTS ...BODY end
```

Where:

- `NAME` is an identifier `/(\.a-zA-Z)+/`.
- `INPUTS` is the number of input registers.
- `OUTPUTS` is the number of output registers.
- `BODY` is a list of labels and instructions.

An instruction takes a number of inputs 
and produces a number of outputs. 
An instruction can take the following forms:

```rust
// ignore all output
RET r2 r3 r4

// capture all output
r1 r2 = RUN step r1 r2

// ignore some output:
r1 _ = RUN step r1 r2
```

An instruction must have the correct number 
of inputs and capture the correct number 
of outputs.

In general:

```rust
r0 r1 ...rN = INS r0 r1 ...rM
------------- optional
```

Here is a list of all operations.

```rust
// Fixed Unsigned Integer Math
ADD 2:1  // Add two regs, F on overflow
SUB 2:1  // Subtract second from first, F on underfloor
MUL 2:1  // Multiply two regs, F on overflow
DIV 2:1  // Divide first by second, F on zero division
SHL 2:1  // Multiply first by 2^second
SHR 2:1  // Divide first by 2^second

// Arbitrary Unsigned Integer Math
ADC 2:2  // Add two regs, output carry result
MLC 2:2  // Multiply two regs, output carry result

// Fixed Signed Integer Math
NTI 1:1  // Convert N64 to S64, F on overflow
ITN 1:1  // Above in reverse, F if negative
NEG 1:1  // flip the sign, F on minimum
ADI 2:1  // Add two regs, F on outflow
SBI 2:1  // Subtract two regs, F on outflow
MLI 2:1  // Multiply two regs, F on outflow
DIV 2:1  // Divide two regs, F when reasonable

// Floating Point Math
NTF 1:1  // Convert N64 to F64, next greater or equal
FTN 1:1  // Above in reverse, F if outflow
STF 1:1  // Convert S64 to N64, next greater or equal

SLF 1:1  // next bigger representable float, F on NaN
SRF 1:1  // next smaller representable float, F on NaN

```

To be continued...
