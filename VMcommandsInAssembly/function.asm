// function functionName 4

// repeat nVars times: push 0

// as with call.asm, we increment A rather than SP, then do SP = SP + nVars at the end
// this time, we are pushing zeros, which is somewhat easier
// By simultaneously setting A and D to addr++, we keep addr in D and can then put it into SP

// use convention of Foo.bar for function bar in file foo

(functionName)
// first block (do if nVars >= 1)
@SP
A=M
M=0  // *SP = 0

// repeat-block (if nVars >= 2, repeat this nVars - 1 times)
AD=A+1 // addr++
M=0

// set SP = addr = SP + nVars = (value stored in A and D)
@SP
M=D 