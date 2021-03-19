// gt  // x > y
	@SP
	AM=M-1  // SP--
	D=M    // D = *SP = y

	A=A-1
	D=M-D // D = x - y
	@NotGreater
	D; JLE  // jump if x - y <= 0 which means x <= y
(Greater)
	@SP
	A=M-1
	M=-1   // *(SP - 1) = 111..1  // top of stack is true
	@EndGreater
	0; JMP
(NotGreater)
	@SP
	A=M-1
	M=0   // *(SP - 1) = 000..0  // top of stack is false
(EndGreater)