// Load a 16 bit number into D (normally can only load a 15 bit num using @val; D=A)

// Load 1000 0000 0000 0001 (0x8001) into D

@16384 // 0100 0000 0000 0000 (0x4000)

D=A    // Load lower 15-bitsBranch if clear

D=D+A  // Left shift by 1

D=D+1  // Add in lsb (not needed, or use D=D, if lsb is 0)