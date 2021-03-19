// if-goto test_label
//
// D = pop()
// @test_label
// D; JLT

// If D == true, then it is 111..1 which is < 0 in two's complement
// Try: D; JNE, thus assuming that D is true unless 0 (this seems to be the assumption made in VMEmulator) // edit: this is how it is supposed to be implemented :)

@SP
AM=M-1  //SP--
D=M
@test_label
D; JNE
