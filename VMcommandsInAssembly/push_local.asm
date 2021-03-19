// push local 10 same principle for [argument, this, that] memory segments
@10
D=A
@LCL
A=D+M  // A = LCL + 10 = addr to collect from
D=M    // D = *(LCL + 10)

@SP
AM=M+1 // SP++
A=A-1
M=D   // *(SP - 1) = D


