# Language Zero

... is an assembly-like language and runtime.

Here is an example:

```rust
@fib 1:1 {
  JGE .else r0 2
  RET r0
.else
  r2 = SUB r0 1
  r3 = SUB r0 2
  r2 = @fib r2
  r3 = @fib r3
  r4 = ADD r2 r3
  RET r4 
}

@start 0:0 {
  r0 = @fib 40
  DBG r0
}
```

This listing computes and displays the 
40th Fibonacci number.

# Functions

A Language Zero module is a list of functions:

```
@NAME INPUTS:OUTPUTS { ...BODY }
```

Where:

- `NAME` is an identifier `/(_a-z)+/`.
- `INPUTS` is the number of input registers.
- `OUTPUTS` is the number of output registers.
- `BODY` is a list of labels and instructions.

## Instructions

An instruction takes a number of inputs 
and produces a number of outputs. 
An instruction can take the following forms:

```
# ignore all output
RET r2 r3 r4

# capture all output
r1 r2 = @step r1 r2

# ignore some output:
r1 _ = @step r1 r2
```

An instruction must have the correct number 
of inputs and capture the correct number 
of outputs.

In general:

```
r0 r1 ...rN = OPC r0 r1 ...rM
------------- optional
```
Where `OPC` is a three-character name,
each character matching `/A-Z/`. 

## Labels

A label is a point, local to a function, 
that can be jumped to from within that function.
A label takes the following form:

```
.NAME
```

where `NAME` is an identifier `/(_a-z)+/`.

# Effect

An effect defines a side effect.
Here are some example effects:

```
# write lower 8 bits as byte to stdout
!put 1:0

# read byte from stdin into register
!get 0:1

# allocate N slots of memory, return pointer
!alloc 1:1

# Free pointer
!free 1:0

# Read slot at pointer
!load 1:1

# Write register into slot at pointer
!store 2:0

# Compute the sha256 of some data
# Passed as string = (ptr, len in bytes)
!sha 2:4
```

To be continued...
