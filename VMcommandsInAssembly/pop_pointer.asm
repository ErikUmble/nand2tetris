// pop pointer 1  // 0->THIS, 1->THAT
@SP
AM=M-1  // Sp--
D=M     // D = *SP

@THAT   // would be @THIS if 0
M=D     // overall -> Foo.15 = *(SP - 1)