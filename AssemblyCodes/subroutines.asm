// how to call a sub-routine from the main program
// contract: store in R0 the value of the return address to goto when done the sub-routine
// this only works when only main can call sub-routines
// to enable recursion and the ability to call sub-routines from other sub-routines
// we need to use a stack, where each function call gets a "scratchpad" with pointer to 
// the address to return to

(Sub_routine)
	// do stuff
	...
	// end the sub-routine by returning to the address specified in R0
	@R0
	A=M 
	0; JMP  // goto the next place in main, as specified in R0

(Main)
	...
	@Return_address
	D=A  // Put the return address in D
	@R0
	M=D  // Store the return address in R0
	@Sub_routine
	0; JMP
	
(Return_address)
	... // can continue main function
