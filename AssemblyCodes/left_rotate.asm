// Rotate is essentially shift, but places the msb into the lsb place 
// Can find if msb is 1 by checking if the number is negative
// Rotate a value in 'data' left by 1

        @lsb

        M=0    // Initialize lsb mask to 0

        @data

        D=M    // Load data value into memory

        @SKIP

        D; JGE // Skip the next step if msb is zero

        @lsb

        M=1    // Set lsb to 1 to match msb 

(SKIP)

        @data

        MD=D+M // Shift data left by 1 (D still has data in it)

        @lsb

        D=D+M  // Add in the lsb

        @data

        M=D    // Store rotated data back in memory

 

        @END

(END)

        0; JMP // Infinite loop to stall simulator