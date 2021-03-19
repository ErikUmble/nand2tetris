// eq  // x == y
	@SP
	AM=M-1  // SP--
	D=M    // D = *SP = y

	A=A-1
	D=D-M  // D = y - x
	@NotEqual
	D; JNE
(Equal)
	@SP
	A=M-1
	M=-1   // *(SP - 1) = 111..1  // top of stack is true
	@EndEqual
	0; JMP
(NotEqual)
	@SP
	A=M-1
	M=0   // *(SP - 1) = 000..0  // top of stack is false
(EndEqual)
	