// pop temp 4
@SP
AM=M-1  // Sp--
D=M     // D = *SP

@R9  // R(5 + 4)
M=D     // overall -> Foo.15 = *(SP - 1)