// return
// contract: caller's saved frame has return address as the topmost (stack-wise) item rather than bottommost
// This is my own way of organizing, which leads to slightly more efficient assembly code // really though, it only is 2 lines of code less, but IMO it's more elegant

// endFrame = LCL  // we simply use LCL to refer to the concept of endFrame
// retAddr = *(endFrame - 1)  // get caller return address // save in case there were no arguments in which case ARG[0] holds the return address
// *ARG = pop()    // put the return value into argument 0 = ARG[0] = *ARG
// SP = ARG + 1 
// THAT = *(endFrame - 2)  // restore caller state
// THIS = *(endFrame - 3) 
// ARG = *(endFrame - 4) 
// LCL = *(endFrame - 5) 
// goto retAddr


// retAddr = *(endFrame - 1)  // get caller return address // save in case there were no arguments in which case ARG[0] holds the return address
@LCL
AM=M-1  // endFrame--
D=M     // D = *(endFrame)
@retAddr
M=D     // retAddr = D

// *ARG = pop()    // put the return value into argument 0 = ARG[0] = *ARG
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

// THAT = *(endFrame - 2)  // restore caller state
@LCL
AM=M-1  // A, M = endFrame--
D=M     // D = *(endFrame)
@THAT
M=D

// THIS = *(endFrame - 3) 
@LCL
AM=M-1  // A, M = endFrame--
D=M     // D = *(endFrame)
@THIS
M=D

// ARG = *(endFrame - 4) 
@LCL
AM=M-1  // A, M = endFrame--
D=M     // D = *(endFrame)
@ARG
M=D

// LCL = *(endFrame - 5) 
@LCL
AM=M-1  // A, M = endFrame--
D=M     // D = *(endFrame)
@LCL
M=D

// goto retAddr
@retAddr
A=M
0; JMP