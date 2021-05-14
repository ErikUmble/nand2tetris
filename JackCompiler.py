"""Assumption: block comments start and end on their own lines"""
import os
import sys

ELEMENTS = {
    element_name: i
    for i, element_name in enumerate(["keyword", "symbol", "integerConstant", "stringConstant", "identifier",
                                      "class", "classVarDec", "type", "subroutineDec", "parameterList",
                                      "subroutineBody", "varDec", "className", "subroutineName", "varName",
                                      "statements", "statement", "letStatement", "ifStatement", "whileStatement",
                                      "doStatement", "returnStatement",
                                      "expression", "term", "subroutineCall", "expressionList", "op", "unaryOp",
                                      "keywordConstant",
                                      ])
}
reverse_elements = {
    i: element_name for element_name, i in ELEMENTS.items()
}
KEYWORDS = ["class", "constructor", "function", "method", "field", "static",
            "var", "int", "char", "boolean", "void", "true", "false", "null", "this",
            "let", "do", "if", "else", "while", "return", "break", "continue"]
SYMBOLS = "{}()[].,;+-*/&|<>=~"
DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
OPS = "+-*/&|<>="
UNARY_OPS = "~-"
BIN_OP_VM_MAP = {"+": "add", "-": "sub", "*": "call Math.multiply 2", "/": "call Math.divide 2",
                 "&": "and", "|": "or", "<": "lt", ">": "gt", "=": "eq"}
UN_OP_VM_MAP = {"~": "not", "-": "neg"}
KEYWORD_CONSTANTS = ["true", "false", "null", "this"]


class SymbolTable:
    """Implements functionality of a symbol table for setting and looking up variables"""

    def __init__(self):
        # ST in form {name: (var_type, var_kind, index), ... }
        self.classST = dict()
        self.subroutineST = dict()
        self.counts = {"local": 0, "argument": 0, "static": 0, "field": 0}

    def define(self, var_name, var_type, var_kind):
        if var_kind in ["local", "argument"]:
            self.subroutineST[var_name] = (var_type, var_kind, self.counts[var_kind])
        elif var_kind in ["static", "field"]:
            self.classST[var_name] = (var_type, var_kind, self.counts[var_kind])
        else:
            raise Exception("Invalid variable kind")

        self.counts[var_kind] += 1
        return self.counts[var_kind] - 1  # return the defined variable's index

    def var_count(self, var_kind):
        if var_kind not in ["local", "argument", "static", "field"]:
            raise Exception("Invalid variable kind")
        return self.counts[var_kind]

    def kind_of(self, var_name):
        """returns the kind of the var_name, or None if it has not been defined"""
        return self.subroutineST.get(var_name, self.classST.get(var_name, (None, None, None)))[1]

    def type_of(self, var_name):
        """returns the type of the var_name, or None if it has not been defined"""
        return self.subroutineST.get(var_name, self.classST.get(var_name, (None, None, None)))[0]

    def index_of(self, var_name):
        """returns the index of the var_name, or None if it has not been defined"""
        return self.subroutineST.get(var_name, self.classST.get(var_name, (None, None, None)))[2]

    def reset_class_symbol_table(self):
        self.classST = dict()
        self.counts["field"] = 0
        self.counts["static"] = 0

    def reset_subroutine_symbol_table(self):
        self.subroutineST = dict()
        self.counts["local"] = 0
        self.counts["argument"] = 0


class JackTokenizer:
    """Implements functionality to advance through a .jack file, getting a token at a time"""

    def __init__(self, filename):
        self.filename = filename
        self.current_token_index = 0
        self.current_token = (None, None)
        self.tokens = []
        self.load_tokens(filename)

    def has_more_tokens(self):
        return self.current_token_index < len(self.tokens)

    def advance(self):
        """advances to the next token and returns it's value and type"""
        self.current_token = self.tokens[self.current_token_index]
        self.current_token_index += 1
        return self.current_token

    def next_token(self):
        """returns the next token value and type without advancing"""
        return self.tokens[self.current_token_index]

    def tokenize_line(self, line):
        """Finds and loads tokens in a line that does not have comments"""
        line = line.strip()
        temp_token = ''
        temp_token_type = None

        def complete_token():
            nonlocal temp_token, temp_token_type
            self.tokens.append(
                (temp_token, temp_token_type)
            )
            temp_token = ''
            temp_token_type = None

        for char in line:
            if temp_token_type == ELEMENTS["integerConstant"]:
                if char in DIGITS:
                    temp_token += char
                else:
                    if int(temp_token) > 32767:
                        raise Exception("Invalid integer constant: " + temp_token + " is > 32767")
                    complete_token()
            elif temp_token_type == ELEMENTS["stringConstant"]:
                if char != '"':
                    temp_token += char
                else:
                    complete_token()
                    continue
            elif temp_token_type == -1:
                if char in LETTERS + DIGITS + '_':
                    temp_token += char
                else:
                    temp_token_type = ELEMENTS["keyword"] if temp_token in KEYWORDS else ELEMENTS["identifier"]

                    complete_token()

            # If we are just starting a new token, we have to figure out what type it is
            if temp_token_type is None:
                temp_token += char
                if char in DIGITS:
                    temp_token_type = ELEMENTS["integerConstant"]
                elif char == '"':
                    temp_token_type = ELEMENTS["stringConstant"]
                    temp_token = ''
                elif char in SYMBOLS:
                    temp_token_type = ELEMENTS["symbol"]
                    complete_token()
                elif char in LETTERS:
                    # could be either a keyword or an identifier
                    temp_token_type = -1
                elif char in ["", " ", "\n"]:
                    temp_token = ''
                else:
                    # the character is not valid in Jack, so we do not include it in the token
                    raise Exception("Invalid character: " + char)

        # make sure we did not miss the last token from the line
        if temp_token != "":
            complete_token()

    def load_tokens(self, filename):
        commenting = False
        with open(filename, "r") as file:
            # We can progress one line at a time, since no tokens can be split across lines
            for line in file:
                if not commenting:
                    if "/*" in line:
                        if "*/" in line:
                            continue
                        else:
                            commenting = True
                            continue
                    line = line.strip().split("//")[0]  # strip whitespace and in-line comments
                    self.tokenize_line(line)
                else:
                    # we need to find the place where commenting stops
                    if "*/" in line:
                        commenting = False


class CompilationEngine:
    """contract: a method is called only if it is known to be the next thing to compile, meaning the callee has
    advanced to see the method's first token or has looked ahead as necessary"""
    def __init__(self, filename=None):
        if filename is not None:
            self.tokenizer = JackTokenizer(filename)
        else:
            self.tokenizer = None
        self.st = SymbolTable()
        self.current_class = ""
        self.num_labels = 0
        self.while_labels = ("", "")

    def compile_class(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        self.st.reset_class_symbol_table()
        code = []
        token, token_type = tokenizer.current_token
        assert(token == "class")
        class_name, token_type = tokenizer.advance()

        assert(token_type == ELEMENTS["identifier"])
        self.current_class = class_name
        token, token_type = tokenizer.advance()

        assert(token == "{")
        token, token_type = tokenizer.advance()

        while token in ["static", "field"]:
            code += self.compile_class_var_dec(tokenizer)  # classVarDec
            token, token_type = tokenizer.advance()  # we only advance when we use a token

        while token in ["constructor", "function", "method"]:
            code += self.compile_subroutine_dec(tokenizer)  # subroutineDec
            token, token_type = tokenizer.advance()

        assert(token == "}")
        assert(not tokenizer.has_more_tokens())
        return code

    def compile_class_var_dec(self, tokenizer=None):
        """Loads class level symbol table from class variable declarations; returns [] no code"""
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token

        # static | field
        assert(token in ["static", "field"])
        var_kind = token
        token, token_type = tokenizer.advance()

        # type
        assert(token in ["int", "char", "boolean"] or token_type == ELEMENTS["identifier"])
        var_type = token
        token, token_type = tokenizer.advance()

        # varName
        assert (token_type == ELEMENTS["identifier"])
        var_name = token
        self.st.define(var_name, var_type, var_kind)
        token, token_type = tokenizer.advance()

        while token == ",":
            # ,
            token, token_type = tokenizer.advance()
            # varName
            assert (token_type == ELEMENTS["identifier"])
            var_name = token
            self.st.define(var_name, var_type, var_kind)
            token, token_type = tokenizer.advance()

        # ;
        assert(token == ";")
        return []

    def compile_subroutine_dec(self, tokenizer=None):
        """returns a list of the vm code commands for this subroutine and re-loads subroutine level symbol table"""
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        self.st.reset_subroutine_symbol_table()

        # Kind of subroutine
        assert(token in ["constructor", "function", "method"])
        current_subroutine_kind = token
        token, token_type = tokenizer.advance()

        if current_subroutine_kind == "method":
            # the first argument in the ST must be the object that the method is applied to
            self.st.define("this", self.current_class, "argument")

        # returnType
        assert (token in ["int", "char", "boolean", "void"] or token_type == ELEMENTS["identifier"])
        token, token_type = tokenizer.advance()

        # subroutineName
        assert(token_type == ELEMENTS["identifier"])
        subroutine_name = self.current_class + "." + token
        token, token_type = tokenizer.advance()

        # (
        assert(token == "(")
        token, token_type = tokenizer.advance()

        if token != ")":
            self.compile_parameter_list(tokenizer)
            token, token_type = tokenizer.advance()

        # )
        assert (token == ")")
        tokenizer.advance()

        function_body = self.compile_subroutine_body(tokenizer)  # save subroutineBody
        code = [get_function(subroutine_name, self.st.var_count("local"))]  # vm function declaration

        # Alloc memory and anchor THIS to the base address if this is a constructor
        if current_subroutine_kind == "constructor":
            code += [get_push("constant", self.st.var_count("field")),
                     get_call("Memory.alloc", 1), get_pop("pointer", 0)]

        # or anchor THIS to the current object passed as the first parameter if method
        elif current_subroutine_kind == "method":
            code += [get_push("argument", 0), get_pop("pointer", 0)]

        code += function_body

        return code

    def compile_parameter_list(self, tokenizer=None):
        """loads argument variables to subroutine level symbol table and returns the number of parameters"""
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        num_params = 0

        # type
        if token in ["int", "char", "boolean", "void"] or token_type == ELEMENTS["identifier"]:
            var_type = token
            token, token_type = tokenizer.advance()

            # varName
            assert(token_type == ELEMENTS["identifier"])
            self.st.define(token, var_type, "argument")
            num_params += 1

            while tokenizer.next_token()[0] == ",":
                # ,
                tokenizer.advance()
                token, token_type = tokenizer.advance()

                # type
                assert (token in ["int", "char", "boolean"] or token_type == ELEMENTS["identifier"])
                var_type = token
                token, token_type = tokenizer.advance()

                # varName
                assert (token_type == ELEMENTS["identifier"])
                self.st.define(token, var_type, "argument")
                num_params += 1
        return num_params

    def compile_subroutine_body(self, tokenizer=None):
        """returns list of vm instructions that complete the body of a vm function"""
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token

        # {
        assert(token == "{")
        code = []
        token, token_type = tokenizer.advance()
        # varDec*
        while token == "var":
            self.compile_var_dec()
            token, token_type = tokenizer.advance()

        # statements
        if token_type in [ELEMENTS["keyword"], ELEMENTS["identifier"]]:
            code += self.compile_statements(tokenizer)
            token, token_type = tokenizer.advance()

        # }
        assert(token == "}")
        return code

    def compile_var_dec(self, tokenizer=None):
        """does not return anything but loads local variables into symbol table
        expects a single Jack instruction of a variable(s) declaration"""
        tokenizer = tokenizer or self.tokenizer

        # var
        assert(tokenizer.current_token[0] == "var")
        token, token_type = tokenizer.advance()

        # type
        assert(token in ["int", "char", "boolean"] or token_type == ELEMENTS["identifier"])
        var_type = token
        token, token_type = tokenizer.advance()

        # varName
        assert (token_type == ELEMENTS["identifier"])
        self.st.define(token, var_type, "local")
        token, token_type = tokenizer.advance()

        while token == ",":
            # ,
            token, token_type = tokenizer.advance()

            # varName
            assert (token_type == ELEMENTS["identifier"])
            self.st.define(token, var_type, "local")
            token, token_type = tokenizer.advance()

        # ;
        assert(token == ";")

    def compile_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        code = []
        if token_type == ELEMENTS["identifier"]:
            # // subroutineCall; or // assignment;
            if tokenizer.next_token()[0] in ["(", "."]:
                # // subroutineCall
                code += self.compile_subroutine_call(tokenizer)
                # since it is like a do statement, dump the returned value
                code.append(get_pop("temp", 0))
            else:
                # // assignment
                assert (tokenizer.next_token()[0] in ["=", "["])
                code += self.compile_assignment(tokenizer)

            token, token_type = tokenizer.advance()
            # ;
            assert (token == ";")

        elif token == "let":
            code += self.compile_let_statement(tokenizer)
        elif token == "if":
            code += self.compile_if_statement(tokenizer)
        elif token == "while":
            code += self.compile_while_statement(tokenizer)
        elif token == "break":
            code += self.compile_break_statement(tokenizer)
        elif token == "continue":
            code += self.compile_continue_statement(tokenizer)
        elif token == "do":
            code += self.compile_do_statement(tokenizer)
        elif token == "return":
            code += self.compile_return_statement(tokenizer)
        else:
            raise Exception("Invalid statement")
        return code

    def compile_statements(self, tokenizer=None):
        """returns a list of vm instructions implementing the following statements, empty list if no statements
        """
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token

        code = []
        while token_type in [ELEMENTS["keyword"], ELEMENTS["identifier"]]:
            code += self.compile_statement(tokenizer)

            # end of statements if the next token does not start a statement
            if tokenizer.next_token()[1] not in [ELEMENTS["keyword"], ELEMENTS["identifier"]]:
                break
            token, token_type = tokenizer.advance()

        return code

    def compile_subroutine_call(self, tokenizer=None):
        """
        // identifier '(' expressionList ')'
        # subroutineName(ExpressionList) | varName.subroutineName(ExpressionList) | className.subroutineName(ExpList)
        code ends by calling the subroutine; does nothing with the returned value
        """
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        code = []
        num_args = 0

        # subroutineName | (className | varName)
        assert (token_type == ELEMENTS["identifier"])
        if tokenizer.next_token()[0] == ".":
            if self.st.kind_of(token) is not None:
                # push the object if this is a varName.methodName() syntax -> ObjectClass.methodName()
                code.append(get_push(self.st.kind_of(token).replace("field", "this"), self.st.index_of(token)))
                num_args += 1
                function_name = self.st.type_of(token)

            else:
                # ClassName.subroutineName() syntax
                function_name = token

            token, token_type = tokenizer.advance()
            assert (token == ".")
            token, token_type = tokenizer.advance()

            # subroutineName
            assert (token_type == ELEMENTS["identifier"])
            function_name += "." + token

        else:
            # subroutineName() syntax -> Foo.subroutineName() if we are in class Foo
            # and we also have to push pointer 0 since the subroutine will be acting on this
            function_name = self.current_class + "." + token
            code.append(get_push("pointer", 0))
            num_args += 1

        token, token_type = tokenizer.advance()

        # (
        assert (token == "(")
        token, token_type = tokenizer.advance()

        # expressionList
        if token != ")":
            returned_stuff = self.compile_expression_list(tokenizer)
            num_args += returned_stuff["num_elements"]
            code += returned_stuff["code"]
            token, token_type = tokenizer.advance()

        # )
        assert (token == ")")

        # add the call function code
        code.append(get_call(function_name, num_args))
        # end of subroutine call
        return code

    def compile_assignment(self, tokenizer=None):
        """
        // varName = expression
        compiled (expression)
        pop var_kind var_index

        or

        // arr[expression1] = expression2
        push arr
        compiled (expression1)
        add                         // top of stack holds address for arr[expression]
        compiled (expression2)
        pop temp 0                  // temp 0 = value of expression2
        pop pointer 1              // anchor THAT to address for arr[expression]
        push temp 0
        pop that 0"""
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token

        # varName
        assert (token_type == ELEMENTS["identifier"] and self.st.kind_of(token) is not None)
        var_name = token
        token, token_type = tokenizer.advance()
        code = []
        # ([ expression ])?
        if token == "[":
            # [
            tokenizer.advance()
            # push arr
            code.append(get_push(self.st.kind_of(var_name).replace("field", "this"), self.st.index_of(var_name)))
            # compiled (expression1)
            code += self.compile_expression(tokenizer)
            # add
            code.append(get_arithmetic("add"))
            token, token_type = tokenizer.advance()

            # ]
            assert (token == "]")
            token, token_type = tokenizer.advance()
            # =
            assert (token == "=")
            tokenizer.advance()

            # compiled (expression2)
            code += self.compile_expression(tokenizer)

            # pop temp 0; pop pointer 1; push temp 0; pop that 0
            code += [get_pop("temp", 0), get_pop("pointer", 1), get_push("temp", 0), get_pop("that", 0)]

        else:
            # =
            assert (token == "=")
            tokenizer.advance()

            # push expression onto stack
            code += self.compile_expression(tokenizer)

            # assign the result of the expression to the variable by pop-ing into the variable
            code.append(get_pop(self.st.kind_of(var_name).replace("field", "this"), self.st.index_of(var_name)))

        return code

    def compile_let_statement(self, tokenizer=None):
        """:returns list of vm commands
        // let assignment;
        """
        tokenizer = tokenizer or self.tokenizer
        # let
        assert(tokenizer.current_token[0] == "let")
        tokenizer.advance()

        code = self.compile_assignment(tokenizer)

        token, token_type = tokenizer.advance()
        # ;
        assert (token == ";")
        return code

    def compile_block(self, tokenizer=None):
        """
        { statements }
        """
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        code = []
        # {
        assert (token == "{")
        token, token_type = tokenizer.advance()

        # compiled statements
        if token_type in [ELEMENTS["keyword"], ELEMENTS["identifier"]]:
            code += self.compile_statements(tokenizer)
            token, token_type = tokenizer.advance()

        # }
        assert (token == "}")
        return code

    def compile_if_statement(self, tokenizer=None):
        """:returns list of vm commands
        handles both {statements} and statement without {}
        // if (expression) {statements1} else {statements2}
            compiled (expression)
            not
            if-goto L1
            compiled (statements1)
            goto L2
        label L1
            compiled (statements2)
        label L2
            ..."""

        tokenizer = tokenizer or self.tokenizer
        # if
        assert (tokenizer.current_token[0] == "if")
        code = []
        token, token_type = tokenizer.advance()

        # Generate L1 and L2
        l1 = "$_IF_FALSE" + str(self.num_labels)
        l2 = "$_IF_END" + str(self.num_labels)
        self.num_labels += 1

        # (
        assert (token == "(")
        tokenizer.advance()

        # push the condition onto stack
        code += self.compile_expression(tokenizer)
        # negate, either by adding a not, or removing one
        if code[-1] == get_arithmetic("not"):
            code.pop(-1)
        else:
            code.append(get_arithmetic("not"))

        code.append(get_if_goto(l1))
        token, token_type = tokenizer.advance()

        # )
        assert (token == ")")
        token, token_type = tokenizer.advance()
        # compile statement or {statements}
        if token == "{":
            code += self.compile_block(tokenizer)
        else:
            assert (token_type in [ELEMENTS["keyword"], ELEMENTS["identifier"]])
            code += self.compile_statement(tokenizer)

        code += [get_goto(l2), get_label(l1)]

        # else
        if tokenizer.next_token()[0] == "else":
            tokenizer.advance()  # eat the else
            token, token_type = tokenizer.advance()

            # compile statement or {statements}
            if token == "{":
                code += self.compile_block(tokenizer)
            else:
                assert (token_type in [ELEMENTS["keyword"], ELEMENTS["identifier"]])
                code += self.compile_statement(tokenizer)

        code.append(get_label(l2))

        return code

    def compile_while_statement(self, tokenizer=None):
        """:returns list of vm commands
        // while (expression) {statements} or // while (expression) statement
        label L1
            compiled (expression)
            not
            if-goto L2
            compiled (statements)
            goto L1
        label L2"""
        tokenizer = tokenizer or self.tokenizer
        # while
        assert (tokenizer.current_token[0] == "while")

        # Generate L1 and L2
        l1 = "$_WHILE_EXP" + str(self.num_labels)
        l2 = "$_WHILE_END" + str(self.num_labels)
        # save previous labels and make the new ones available for use of break and continue within the statments block
        (previous_l1, previous_l2) = self.while_labels
        self.while_labels = (l1, l2)
        self.num_labels += 1

        code = [get_label(l1)]
        token, token_type = tokenizer.advance()

        # (
        assert (token == "(")
        tokenizer.advance()

        # compiled expression; not; if-goto L2
        code += self.compile_expression(tokenizer) + [get_arithmetic("not"), get_if_goto(l2)]
        token, token_type = tokenizer.advance()

        # )
        assert (token == ")")

        token, token_type = tokenizer.advance()

        # compile statement or {statements}
        if token == "{":
            code += self.compile_block(tokenizer)
        else:
            assert (token_type in [ELEMENTS["keyword"], ELEMENTS["identifier"]])
            code += self.compile_statement(tokenizer)

        # re-instate outer while loop labels
        self.while_labels = (previous_l1, previous_l2)

        code += [get_goto(l1), get_label(l2)]
        return code

    def compile_break_statement(self, tokenizer=None):
        """:returns a list with the goto command to exit the current innermost while loop"""
        tokenizer = tokenizer or self.tokenizer
        # break
        assert (tokenizer.current_token[0] == "break")
        token, token_type = tokenizer.advance()

        # ;
        assert (token == ";")
        assert (self.while_labels[1] != "")
        return [get_goto(self.while_labels[1])]

    def compile_continue_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        # continue
        assert (tokenizer.current_token[0] == "continue")
        token, token_type = tokenizer.advance()

        # ;
        assert (token == ";")
        assert (self.while_labels[0] != "")
        return [get_goto(self.while_labels[0])]

    def compile_do_statement(self, tokenizer=None):
        """returns a list of vm commands to call the subroutine specified by the do statement
        // do subroutineCall;
        """
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        # do
        assert(token == "do")
        tokenizer.advance()

        # subroutineCall
        code = self.compile_subroutine_call(tokenizer)

        # since it is a do statement, dump the returned value
        code.append(get_pop("temp", 0))
        token, token_type = tokenizer.advance()
        # ;
        assert (token == ";")
        return code

    def compile_return_statement(self, tokenizer=None):
        """:returns a list of vm commands for putting return value on stack, then returning"""
        tokenizer = tokenizer or self.tokenizer
        # return
        assert (tokenizer.current_token[0] == "return")
        code = []
        token, token_type = tokenizer.advance()

        # expression
        if token != ";":
            code += self.compile_expression(tokenizer)
            token, token_type = tokenizer.advance()
        else:  # void method
            code.append(get_push("constant", 0))

        # ;
        assert (token == ";")

        code.append(get_return())
        return code

    def compile_expression(self, tokenizer=None):
        """:returns a list of vm commands that result in the value of the expression on the top of the stack"""
        tokenizer = tokenizer or self.tokenizer

        code = self.compile_term(tokenizer)

        # op
        while tokenizer.next_token()[0] in OPS:
            token, token_type = tokenizer.advance()
            this_bin_op = token
            tokenizer.advance()
            # term
            code += self.compile_term(tokenizer)
            code.append(get_arithmetic(BIN_OP_VM_MAP[this_bin_op]))

        return code

    def compile_term(self, tokenizer=None):
        """:returns a list of vm commands that result in the value of the term on the top of the stack"""
        tokenizer = tokenizer or self.tokenizer
        code = []
        token, token_type = tokenizer.current_token

        # is it a simple term?
        if token_type == ELEMENTS["integerConstant"]:
            code.append(get_push("constant", token))  # such as push constant 5 for token=5

        elif token_type == ELEMENTS["stringConstant"]:
            '''
            "hello" requires String.new(5), and 5 calls to String.appendChar(this_string, char_of_hello)
            '''
            # push length of string; call String.new 1;
            code += [get_push("constant", len(token)), get_call("String.new", 1)]

            # String.appendChar maintains the string address on the top of the stack
            for char in token:
                code += [get_push("constant", ord(char)), get_call("String.appendChar", 2)]

        elif token in KEYWORD_CONSTANTS:
            # standard mapping of constants
            if token in ["false", "null"]:
                code.append(get_push("constant", "0"))
            elif token == "true":
                code += [get_push("constant", "0"), get_arithmetic("not")]  # -1 = not false
            elif token == "this":
                code.append(get_push("pointer", 0))

        elif token in UNARY_OPS:
            this_unary_op = token  # - or ~
            tokenizer.advance()
            # first push term, then apply unary operation
            code += self.compile_term(tokenizer)  # term
            code.append(get_arithmetic(UN_OP_VM_MAP[this_unary_op]))

        elif token == "(":
            # (
            tokenizer.advance()
            code += self.compile_expression(tokenizer)  # expression
            token, token_type = tokenizer.advance()

            # )
            assert (token == ")")

        elif token_type == ELEMENTS["identifier"]:
            # could be varName | varName[expression] |
            # subroutineName(expressionList) | varName.subroutineName(expressionList)
            next_token = tokenizer.next_token()[0]
            if next_token == "[":
                # var_name[expression] syntax ->
                ''' 
                push varName
                push expression
                add
                pop pointer 1  // anchor THAT to the value of the pointer varName + result of expression inside []
                push that 0
                '''
                # varName
                assert(self.st.kind_of(token) is not None)  # ensure that this is a variable
                code.append(get_push(self.st.kind_of(token).replace("field", "this"), self.st.index_of(token)))
                token, token_type = tokenizer.advance()
                
                # [
                assert(token == "[")
                tokenizer.advance()

                # push expression
                code += self.compile_expression(tokenizer)
                token, token_type = tokenizer.advance()

                # ]
                assert (token == "]")

                # add; pop pointer 1; push that 0
                code += [get_arithmetic("add"), get_pop("pointer", 1), get_push("that", 0)]

            elif next_token == "(" or next_token == ".":
                # ClassName.subroutineName() | varName.methodName() | subroutineName() syntax
                code += self.compile_subroutine_call(tokenizer)
                # since this is in an expression, we leave the returned value on the stack

            else:
                # varName  # if the variable is a field variable, we use the 'this' memory segment
                code.append(get_push(self.st.kind_of(token).replace("field", "this"), self.st.index_of(token)))

        return code

    def compile_expression_list(self, tokenizer=None):
        """returns {"code": list of vm commands, "num_elements": number of expressions}"""
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        code = []
        num_elements = 0
        if token != ")":

            code += self.compile_expression(tokenizer)
            num_elements += 1

            while tokenizer.next_token()[0] == ",":
                tokenizer.advance()
                # ,
                tokenizer.advance()
                # expression
                code += self.compile_expression(tokenizer)
                num_elements += 1

        return {"code": code, "num_elements": num_elements}


def get_push(mem_seg, index):
    return f"push {mem_seg} {index}"


def get_pop(mem_seg, index):
    return f"pop {mem_seg} {index}"


def get_arithmetic(operation):
    return operation


def get_label(label_name):
    return f"label {label_name}"


def get_goto(label_name):
    return f"goto {label_name}"


def get_if_goto(label_name):
    return f"if-goto {label_name}"


def get_call(function_name, num_args):
    return f"call {function_name} {num_args}"


def get_function(function_name, num_locals):
    return f"function {function_name} {num_locals}"


def get_return():
    return "return"


def main(file_or_dir):
    """Parses the XXX.jack file or every filename1.jack, filename2.jack, etc file in the directory
     For every XXX.jack file, generates an XXX.xml file containing the parse tree of the XXX.jack file
     and an XXXT.xml file that contains the parsing of all the tokens in the XXX.jack file"""
    input_files_paths = []
    files_names = []
    if os.path.isdir(file_or_dir):
        for (dirpath, dirnames, filenames) in os.walk(file_or_dir):
            for file in filenames:
                if file.endswith(".jack"):
                    input_files_paths.append(os.path.join(dirpath, file))
                    files_names.append(os.path.basename(file)[:-5])

    elif file_or_dir.endswith(".jack"):
        input_files_paths = [file_or_dir]
        files_names.append(file_or_dir[:-5])
    else:
        print("Usage python JackCompiler filename.jack || python JackCompiler my_directory/ ")
        return

    # Compile
    for i, path in enumerate(input_files_paths):
        ''''# put results in current directory
        with open(files_names[i] + ".vm", "w") as vm:
            compiler = CompilationEngine(path)
            assert(compiler.tokenizer.advance()[0] == "class")
            for code_line in compiler.compile_class():
                if code_line == "":
                    continue
                vm.write(code_line + "\n")'''

        # put the results in their original directory
        with open(path[:-5] + ".vm", "w") as vm:
            compiler = CompilationEngine(path)
            assert(compiler.tokenizer.advance()[0] == "class")
            for code_line in compiler.compile_class():
                if code_line == "":
                    continue
                vm.write(code_line + "\n")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler (file.jack | directory)")
        sys.exit(1)
    main(sys.argv[1])
