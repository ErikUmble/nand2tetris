// return

// endFrame = LCL  
// retAddr = *(endFrame - 5)  // get caller return address // save in case there were no arguments in which case ARG[0] holds the return address
// *ARG = pop()    // put the return value into argument 0 = ARG[0] = *ARG
// SP = ARG + 1 
// THAT = *(endFrame - 1)  // restore caller state
// THIS = *(endFrame - 2) 
// ARG = *(endFrame - 3) 
// LCL = *(endFrame - 4) 
// goto retAddr

// we can simply use LCL the same way that endFrame is used above, since LCL is not updated until the end

// set retAddr = *(LCL - 5) 
@LCL
D=M
@5
A=D-A  // A = LCL - 5
D=M    // D = *(LCL - 5) = val
@retAddr
M=D   // retAddr = D

// *ARG = pop()
@SP
A=M-1 
D=M  // D = *(SP - 1) = value on top of stack = return value
@ARG
A=M
M=D  // *ARG = D 

// SP = ARG + 1
@ARG
D=M+1 // D = ARG + 1
@SP
M=D

// THAT = *(endFrame - 1)
@LCL
AM=M-1  // A, M = endFrame - 1  // endFrame--
D=M    // D = *(endFrame - 1)
@THAT  // A = addr
M=D   // THAT = D

// THIS = *(endFrame - 2) 
@LCL
AM=M-1  // A, M = endFrame - 2  // endFrame--
D=M    // D = *(endFrame - 2)
@THIS  // A = addr
M=D   // THAT = D

// ARG = *(endFrame - 3) 
@LCL
AM=M-1  // A, M = endFrame - 3  // endFrame--
D=M    // D = *(endFrame - 3)
@ARG  // A = addr
M=D   // THAT = D

// LCL = *(endFrame - 4)
@LCL
AM=M-1  // A, M = endFrame - 4  // endFrame--  // now *LCL = saved_LCL
D=M    // D = *(endFrame - 4)
@LCL  // A = addr
M=D   // THAT = D

// goto retAddr
@retAddr
A=M 
0; JMP