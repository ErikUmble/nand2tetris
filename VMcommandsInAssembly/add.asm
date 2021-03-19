// add
@SP
AM=M-1  // SP--
D=M     // D = *SP

A=A-1
M=D+M   // M = D + *(SP - 1)  // RAM[SP - 1] = RAM[SP] + RAM[SP - 1]

// SP was decreased to point at the top item from the stack
// which was stored in D
// then A (which was the value of the decreased SP) was decreased by one
// so that the memory being accessed was the second item on stack
// then we re-assigned that memory to the sum of it and D (which contained the val of top item)
// then we are done, since stack pointer is pointing at that previously top item (garbage value) 
// which is where we will store the next item to push on stack
