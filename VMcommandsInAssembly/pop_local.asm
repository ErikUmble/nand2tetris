// pop local 20
@20
D=A 
@LCL
D=D+M 
@addr
M=D      // addr = LCL + 20

@SP
AM=M-1  // SP--
D=M     // D = *SP

@addr
A=M 
M=D  // *addr = D
