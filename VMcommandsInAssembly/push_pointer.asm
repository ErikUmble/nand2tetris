// push pointer 0  // 0->THIS, 1->THAT

@THIS  // would be @THAT if 1
D=M
@SP
AM=M+1  // SP++
A=A-1
M=D     // *(SP - 1) = Foo.13