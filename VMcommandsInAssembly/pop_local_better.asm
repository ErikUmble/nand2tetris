// pop local 7  // same principle for [argument, this, that] memory segments
@7
D=A 
@LCL
D=D+M  // D = LCL + 7

@SP
AM=M-1  // SP--
D=D+M     // D = *SP + LCL + 7 // D = val + addr

A=D-M  // A = val + addr - val so A = addr
M=D-A  // RAM[addr] = val + addr - addr = val
