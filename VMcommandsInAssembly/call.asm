// call functionName 3

// 	push returnAddress
//	push LCL
//	push ARG
//	push THIS
//	push THAT
//	ARG = SP - 5 - nArgs
//	LCL = SP
//	goto functionName
//(returnAddress)

// rather than using the overhead of push commands (that increment SP each time)
// we increment D=A+1=addr (then doing the variable swap), which is cheaper, then updates SP = SP + 5 after
// this means we can do ARG = SP before updating SP

@returnAddress
D=A
@SP
A=M
M=D   // *(SP) = returnAddress

// push LCL
// want RAM[addr] = val  (since val is stored in LCL we will achieve this efficiently with the following variables swap)
D=A+1 // D = addr // addr = next spot to push
@LCL
D=D+M // D = addr + val
A=D-M // A = addr + val - val so A = addr
M=D-A // RAM[addr] = addr + val - addr so RAM[addr] = val which is what we want

// we use the same technique for each of the other pushes

// push ARG
D=A+1 // D = addr // addr = next spot to push
@ARG
D=D+M // D = addr + val
A=D-M // A = addr + val - val so A = addr
M=D-A // RAM[addr] = addr + val - addr so RAM[addr] = val which is what we want

// push THIS
D=A+1 // D = addr // addr = next spot to push
@THIS
D=D+M // D = addr + val
A=D-M // A = addr + val - val so A = addr
M=D-A // RAM[addr] = addr + val - addr so RAM[addr] = val which is what we want

// push THAT
D=A+1 // D = addr // addr = next spot to push
@THAT
D=D+M // D = addr + val
A=D-M // A = addr + val - val so A = addr
M=D-A // RAM[addr] = addr + val - addr so RAM[addr] = val which is what we want

// set ARG = SP - nArgs
@SP
D=M
@3   //////// @nArgs
D=D-A  // D = SP - 3
@ARG
M=D  // ARG = D 

// Set SP, LCL = SP + 5
@5
D=A   // D = 5
@SP
MD=M+D  // D,SP = 5 + SP

@LCL
M=D  // LCL = D

// goto functionName
@functionName
0; JMP

(returnAddress)
