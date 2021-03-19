// Efficient Mult: implements shift-add algorithm
// Efficienty edit: no longer calls create_mask, but updates mask in main
// Add is simplified, as there is no longer a main function calling other sub-routines

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
	
	// mask starts as 0000000000000001 and is shifted each iteration
	@mask
	M=1

(Add)
	@n 
	D=M 
	@sum
	M=M+D  // sum += n
	
	//return
	@Return_from_add
	0; JMP
	
(Loop)
	// Check if i == 16 (bit length of numbers being multiplied)
	@i 
	D=M 
	@16      // can replace 16 with 32 or 64 for 32 or 64 bit machines respectively
	D=D-A
	@End
	D; JEQ  // goto end if i == 16

	// if mask&m != 0, then we must add the ith shift of n to sum by calling Add		
	@m 
	D = M 
	@mask
	D = D&M  // D = mask & m 
	
	@Add
	D; JNE  // call Add if mask & m != 0
	
(Return_from_add)
	// Finish this iteration by shifting n,mask and incrementing i 
	@n 
	D=M 
	M=D+M  // n = n + n  (n is shifted to the left when multiplied by 2)
	
	@mask
	D=M
	M=D+M 
	
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
			