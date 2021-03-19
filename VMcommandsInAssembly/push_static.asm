// push static 13
// assuming this command is found in Foo.vm
@Foo.13
D=M
@SP
AM=M+1  // SP++
A=A-1
M=D     // *(SP - 1) = Foo.13
