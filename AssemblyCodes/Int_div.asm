// Int_Div.asm Computes integer division
// Implements algorithm described in https://en.wikipedia.org/wiki/Division_algorithm
// Inputs: R0 to be divided by R1
// Outputs: R2 will contain R0//R1 (integer quotient), and R3 will contain R0%R1 (remainder)

// Initialize Variables
	@R0
	D=M
	@n
	M=D  //n=R0 (numerator)
	
	@R1
	D=M
	@d 
	M=D  //d=R1 (divisor)
	
	@q
	M=0
	@r 
	M=0
	
	@16
	D=A
	@i 
	M=D  // Set i to 16 (the number of bits)
	
	
	// least significant bit mask = 0000000000000001
	@lsb_mask 
	M=1
	
	// mask will be generated during run time, as i goes from n-1 to 0
	@mask
	M=0

// Begin with Main
	@Main
	0; JMP
	
(Create_mask)
			@mask
			M=1    // Initial mask with b0 set
			@bit
			M=D    // Store bit position in memory
			@MASKTEST
			0; JMP // Jump to test at end of loop

	(MASKLOOP)

			@mask
			D=M    // get copy of mask in D and M
			MD=D+M // Double mask to left shift by 1
			@bit
			MD=M-1 // decrement bit position (i.e., shift amount)

	(MASKTEST)
			
			@MASKLOOP
			D; JGT // Stay in loop if shift amount is still >0
			@Return_from_mask
			0; JMP //return to return address
			
(Main)
	(Loop)
		// Decrement i (so that it starts at n-1) and confirm that i >= 0
		@i
		MD=M-1
		
		@End
		D; JLT  // goto end if i < 0
		
		// generate the i'th mask to use during this loop
		// D still holds i
		@Create_mask
		0; JMP
	
	(Return_from_mask)
	
		// Left shift r 
		@r 
		D=M 
		M=M+D 
		
		// Set the r[0] to equal n[i] 
		@n 
		D=M 
		@mask
		D = D & M 
		
		// continue to Case1 unless mask&n == 0
		@Case2
		D; JEQ
		
	(Case1) // n[i] == 1 in other words (mask & n) != 0
		// Set r to equal r | lsb_mask to update r[0] if it was a 0
		@lsb_mask
		D=M
		@r 
		M=M|D 
		
		@Return_from_case
		0; JMP
		
	(Case2) // n[i] != 1
		// Set r to equal r & (!lsb_mask)  to make r[i] = 0
		@lsb_mask
		D=!M 
		@r 
		M=M&D 
		
	(Return_from_case)
		// Check to see if r >= d
		@r 
		D=M 
		@d 
		D=D-M 
	
		@Skip_r_greater
		D; JLT  // skip r >= d if r-d < 0
	(R_greater)
		
		@d 
		D=M 
		@r 
		M=M-D  // r = r-d
		
		// Set q[i] = 1  by q = q | mask
		@mask
		D=M 
		@q 
		M=M|D
	
	(Skip_r_greater)
	
		@Loop
		0; JMP
		
(End)
	@q
	D=M 
	@R2
	M=D  // R2 = quotient
	
	@r 
	D=M 
	@R3
	M=D  // R3 = remainder
	
(Inf_loop)
	@Inf_loop
	0; JMP