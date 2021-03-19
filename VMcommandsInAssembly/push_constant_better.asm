// push constant 5
@5
D=A  // D = constant 5
@SP
AM=M+1  // SP++
A=A-1
M=D  // *(SP - 1) = 5

// this is more efficient, as it is cheaper to increment SP while setting A to it, then decrementing A
// rather than @SP twice
