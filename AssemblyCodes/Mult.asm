// Efficient Mult: implements shift-add algorithm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

// R2 holds the sum

// Initialize Variables
	@sum
	M=0
	
	@R0
	D=M
	@n 
	M=D // Set n to the value of R0
	
	@R1
	D=M
	@m 
	M=D // Set m to the value of R1
	
	@i 
	M=0
	
	@mask
	M=1
	
	@bit
	M=0
	
	
// Begin with Main
	@Main
	0; JMP

(Add) 
	// sub-routine to add the value of the n register to sum
	// contract: store return address in R4 before calling this
	// internal-variables: n:read, sum:read/write, R4:read(return address)
	@n
	D=M
	@sum
	M = D+M // sum += n
	
	// return
	@R4
	A=M
	0; JMP

(Create_mask)
	// sub-routine to generate a mask (00..), but with the D'th bit set to 1
	// ie. if D=3 D=3 mask will end up storing 0000000000001000 (in the [3] place)
	// contract: store return address in R4 before calling this
	// the finished mask will be stored in @mask and in D
	// internal-variables: mask,bit:read/write, R0:read(return address)
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
			@mask
			D=M    // put finished mask in D
			@R4
			A=M
			0; JMP //return to return address
(Main)
	
	(Loop)
			// Check if i == 16 (bit length of numbers being multiplied)
			@i 
			D=M 
			@16      // can replace 16 with 32 or 64 for 32 or 64 bit machines respectively
			D=D-A
			@End
			D; JEQ  // goto end if i == 16
		
			// Create mask of the ith bit
			@Return_from_mask
			D=A
			@R4
			M=D  // Set R4 to the instruction address Return_from_mask
			
			@i
			D=M // Set D=i according to create_mask contract
			
			@Create_mask
			0; JMP  // call sub-routine create_mask
			
	
		(Return_from_mask)
			// if mask&m != 0, then we must add the ith shift of n to sum by calling Add
			@Return_from_add
			D = A 
			@R4
			M = D  // Set R4 to the instruction address of Return_from_add
			
			@m 
			D = M 
			@mask
			D = D&M  // D = mask & m 
			
			@Add
			D; JNE  // call Add if mask & m != 0
			
		(Return_from_add)
			// Finish this iteration by shifting n and incrementing i 
			@n 
			D=M 
			M=D+M  // n = n + n  (n is shifted to the left when multiplied by 2)
			
			@i
			M = M+1  //i++
			
			@Loop
			0; JMP
		
(End)
	@sum
	D=M
	@R2
	M=D  // Set R2 to the computed product
	
	@End
	0; JMP  // Infinite loop
			