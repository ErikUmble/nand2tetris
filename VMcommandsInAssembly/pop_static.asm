// pop static 15
// assuming this command is found in Foo.vm
@SP
AM=M-1  // Sp--
D=M     // D = *SP

@Foo.15
M=D     // overall -> Foo.15 = *(SP - 1)