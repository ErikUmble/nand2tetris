// sub
@SP
AM=M-1  // SP--
D=M     // D = *SP

A=A-1
M=M-D   // M = *(SP - 1) - D  // RAM[SP - 1] = RAM[SP - 1] - RAM[SP] = x - y (assuming y was top on stack)