// http://www.dragonwins.com/domains/getteched/csm/CSCI410/references/hack.htm
// ==========================================================

// ROTL1

// ----------------------------------------------------------

// Description:

//    Rotates the value in the D register left 1 bit

// ----------------------------------------------------------

// Arguments:

//    D  - value to be rotated

//    R0 - Return address

// Return values:

//    D  - rotated value

// Local variables:

//    R1 - data being worked on

//    R2 - lsb value to be added to shift to finish rotate

// ----------------------------------------------------------

 

(ROTL1)

        @R2

        M=0    // Initialize lsb mask to 0

        @R1

        D=M    // Load data value into memory

        @ROTL1_SKIP

        D; JGE // Skip the next step if msb is zero

        @R2

        M=1    // Set lsb to 1 to match msb 

(ROTL1_SKIP)

        @R1

        MD=D+M // Shift data left by 1 (D still has data in it)

        @R2

        D=D+M  // Add in the lsb

        @R0    // R0 is NOT the return address

        A=M    // It is were the return address is stored 

        0; JMP // Return to calling code

 

// ==========================================================

// ==========================================================

// MAIN

// ----------------------------------------------------------

// Description:

//    Main code that uses the ROTL1 to rotate a value left

//    by an arbitrary amount

// ----------------------------------------------------------

// Arguments:

//    R0 - value to be rotated

//    R1 - amount to rotate by

// Return values:

//    D  - rotated value

// ----------------------------------------------------------

 

(MAIN)

        // Set up the memory with some test data

        @100   // Value to be rotated

        D=A

        @R0    // R0 holds the value to be rotated

        M=D 

        @7     // Number of positions to rotate the value

        D=A   

        @R1    // R1 holds the rotate amount

        M=D

 

        // Loop to rotate value in R1 the amount in R0

(MAIN_TEST)

        @R1

        D=M

        @MAIN_LOOP_END

        D;JLE  // Exit loop when shift amount is <=0

 

        // --------------------------------------------------

        // Use ROTL1 to rotate value in D left 1 bit

        // --------------------------------------------------

 

        // Transfer scratchpad registers to safe area

        @R0    // Transfer R0 to R8

        D=M

        @R8

        M=D

        @R1    // Transfer R1 to R9

        D=M

        @R9

        M=D

 

        // CALL ROTL1

        @RET_A

        D=A    // Put Return Address in D

        @R0

        M=D    // Store Return Address stored in R0

        @R8

        D=M    // Get desired value in D (from safe store)

        @ROTL1

        0; JMP // Call ROTL1

(RET_A)

 

        // Plase return value into scratchpad

        @R0    // Return value in D goes into R0

        M=D   

 

        // Restore rest of scratchpad

        @R9 // Transfer R9 to R1

        D=M

        @R1

        M=D

 

        // --------------------------------------------------

 

        @R1

        MD=M-1 // Decrement rotate amount

        @MAIN_TEST

        0; JMP 

 

(MAIN_LOOP_END)

        @R1

        D=M    // Final rotated amount is in D

 

        @END

(END)

        0; JMP // Infinite loop to stall simulator