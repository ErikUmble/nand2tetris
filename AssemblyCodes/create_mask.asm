// http://www.dragonwins.com/domains/getteched/csm/CSCI410/references/hack.htm

// Create a mask with bit n set where n is in D register
// ie. if D=3 mask will end up storing 0000000000001000 (in the [3] place)

        @mask

        M=1    // Initial mask with b0 set

        @bit

        M=D    // Store bit position in memory

        @TEST

        0; JMP // Jump to test at end of loop

(LOOP)

        @mask

        D=M    // get copy of mask in D and M

        MD=D+M // Double mask to left shift by 1

        @bit

        MD=M-1 // decrement bit position (i.e., shift amount)

(TEST)
		
		@LOOP
        D; JGT // Stay in loop if shift amount is still >0

        @mask

        D=M    // put finished mask in D

 

        @END

(END)

        0; JMP // Infinite loop to stall simulator