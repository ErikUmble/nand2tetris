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
            "let", "do", "if", "else", "while", "return"]
SYMBOLS = "{}()[].,;+-*/&|<>=~"
DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
OPS = "+-*/&|<>="
UNARY_OPS = "~-"
KEYWORD_CONSTANTS = ["true", "false", "null", "this"]


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


def terminal_xml_format(token, token_type, specification=None, st=None):
    token_element = reverse_elements[token_type]
    if token_element == "identifier":
        if specification is None:
            if st is not None:
                if st.kind_of(token) is not None:
                    specification = "-".join(["", token, st.type_of(token),
                                              st.kind_of(token), str(st.index_of(token)), "use"])
                else:
                    specification = "-className-use"
            else:
                specification = ""
        token_element += specification
    # note: we replace the & first, so that it does not then replace all the other replacements
    xml_token = token.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"<{token_element}> {xml_token} </{token_element}>"


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

    def reset_classST(self):
        self.classST = dict()

    def reset_subroutineSt(self):
        self.subroutineST = dict()


class CompilationEngine:
    """contract: a method is called only if it is known to be the next thing to compile, meaning the callee has
    advanced to see the method's first token or has looked ahead as necessary"""

    def __init__(self, filename=None):
        if filename is not None:
            self.tokenizer = JackTokenizer(filename)
        else:
            self.tokenizer = None
        self.st = SymbolTable()

    def compile_class(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        self.st.reset_classST()
        token, token_type = tokenizer.advance()
        assert (tokenizer.current_token[0] == "class")

        code = ["<class>", terminal_xml_format(token, token_type)]  # class
        class_name, token_type = tokenizer.advance()

        assert (token_type == ELEMENTS["identifier"])

        code.append(terminal_xml_format(class_name, token_type, "-class-def"))  # className
        token, token_type = tokenizer.advance()

        assert (token == "{")
        code.append(terminal_xml_format(token, token_type))  # {
        token, token_type = tokenizer.advance()

        while token in ["static", "field"]:
            code += self.compile_class_var_dec(tokenizer)  # classVarDec
            token, token_type = tokenizer.advance()  # we only advance when we use a token

        while token in ["constructor", "function", "method"]:
            code += self.compile_subroutine_dec(tokenizer)  # subroutineDec
            token, token_type = tokenizer.advance()  # we only advance when we use a token

        assert (token == "}")
        code.append(terminal_xml_format(token, token_type))  # }

        code.append("</class>")
        return code

    def compile_class_var_dec(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        assert (token in ["static", "field"])
        var_kind = token
        code = ["<classVarDec>", terminal_xml_format(token, token_type)]  # static | field
        token, token_type = tokenizer.advance()

        assert (token in ["int", "char", "boolean"] or token_type == ELEMENTS["identifier"])
        var_type = token
        code.append(terminal_xml_format(token, token_type))  # type
        token, token_type = tokenizer.advance()

        assert (token_type == ELEMENTS["identifier"])
        var_name = token
        var_index = self.st.define(var_name, var_type, var_kind)
        code.append(terminal_xml_format(token, token_type,
                                        "-".join(["", var_name, var_type, var_kind, str(var_index), "def"])))  # varName
        token, token_type = tokenizer.advance()

        while token == ",":
            code.append(terminal_xml_format(token, token_type))  # ,
            token, token_type = tokenizer.advance()
            assert (token_type == ELEMENTS["identifier"])
            var_name = token
            var_index = self.st.define(var_name, var_type, var_kind)
            code.append(terminal_xml_format(token, token_type,
                                            "-".join(
                                                ["", var_name, var_type, var_kind, str(var_index), "def"])))  # varName
            token, token_type = tokenizer.advance()

        assert (token == ";")
        code.append(terminal_xml_format(token, token_type))  # ;

        code.append("</classVarDec>")
        return code

    def compile_subroutine_dec(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        self.st.reset_subroutineSt()
        code = ["<subroutineDec>"]
        assert (token in ["constructor", "function", "method"])
        code.append(terminal_xml_format(token, ELEMENTS["keyword"]))
        token, token_type = tokenizer.advance()

        assert (token in ["int", "char", "boolean", "void"] or token_type == ELEMENTS["identifier"])
        code.append(terminal_xml_format(token, token_type))  # returnType
        token, token_type = tokenizer.advance()

        assert (token_type == ELEMENTS["identifier"])
        code.append(terminal_xml_format(token, token_type, "-subroutine-def"))  # subroutineName
        token, token_type = tokenizer.advance()

        assert (token == "(")
        code.append(terminal_xml_format(token, token_type))  # (
        token, token_type = tokenizer.advance()

        if token != ")":
            code += self.compile_parameter_list(tokenizer)
            token, token_type = tokenizer.advance()

        assert (token == ")")
        code.append(terminal_xml_format(token, token_type))  # )
        tokenizer.advance()

        code += self.compile_subroutine_body(tokenizer)  # subroutineBody

        code.append("</subroutineDec>")
        return code

    def compile_parameter_list(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        code = ["<parameterList>"]
        if token in ["int", "char", "boolean", "void"] or token_type == ELEMENTS["identifier"]:
            var_type = token
            code.append(terminal_xml_format(token, token_type))  # type
            token, token_type = tokenizer.advance()

            assert (token_type == ELEMENTS["identifier"])
            self.st.define(token, var_type, "argument")
            code.append(terminal_xml_format(token, token_type, "-".join(["", token,
                                                                         self.st.type_of(token),
                                                                         self.st.kind_of(token),
                                                                         str(self.st.index_of(token))],
                                                                        "def")))  # varName

            while tokenizer.next_token()[0] == ",":
                token, token_type = tokenizer.advance()
                code.append(terminal_xml_format(token, token_type))  # ,
                token, token_type = tokenizer.advance()

                assert (token in ["int", "char", "boolean"] or token_type == ELEMENTS["identifier"])
                var_type = token
                code.append(terminal_xml_format(token, token_type))  # type
                token, token_type = tokenizer.advance()

                assert (token_type == ELEMENTS["identifier"])
                self.st.define(token, var_type, "argument")
                code.append(terminal_xml_format(token, token_type, "-".join(["", token,
                                                                             self.st.type_of(token),
                                                                             self.st.kind_of(token),
                                                                             str(self.st.index_of(token)),
                                                                             "def"])))  # varName

        code.append("</parameterList>")
        return code

    def compile_subroutine_body(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        assert (token == "{")
        code = ["<subroutineBody>", terminal_xml_format(token, ELEMENTS["symbol"])]  # {
        token, token_type = tokenizer.advance()
        # varDec*
        while token == "var":
            code += self.compile_var_dec(tokenizer)
            token, token_type = tokenizer.advance()

        # statements
        if token in ["let", "if", "while", "do", "return"]:
            code += self.compile_statements(tokenizer)
            token, token_type = tokenizer.advance()

        assert (token == "}")
        code.append(terminal_xml_format(token, token_type))  # }

        code.append("</subroutineBody>")
        return code

    def compile_var_dec(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        assert (tokenizer.current_token[0] == "var")
        code = ["<varDec>", terminal_xml_format("var", ELEMENTS["keyword"])]  # var
        token, token_type = tokenizer.advance()

        assert (token in ["int", "char", "boolean"] or token_type == ELEMENTS["identifier"])
        var_type = token
        code.append(terminal_xml_format(token, token_type, st=self.st))  # type
        token, token_type = tokenizer.advance()

        assert (token_type == ELEMENTS["identifier"])
        self.st.define(token, var_type, "local")
        code.append(terminal_xml_format(token, token_type, "-".join(["", token,
                                                                     self.st.type_of(token),
                                                                     self.st.kind_of(token),
                                                                     str(self.st.index_of(token)),
                                                                     "def"])))  # varName
        token, token_type = tokenizer.advance()

        while token == ",":
            code.append(terminal_xml_format(token, token_type))  # ,
            token, token_type = tokenizer.advance()

            assert (token_type == ELEMENTS["identifier"])
            self.st.define(token, var_type, "local")
            code.append(terminal_xml_format(token, token_type, "-".join(["", token,
                                                                         self.st.type_of(token),
                                                                         self.st.kind_of(token),
                                                                         str(self.st.index_of(token)),
                                                                         "def"])))  # varName
            token, token_type = tokenizer.advance()

        assert (token == ";")
        code.append(terminal_xml_format(token, token_type))  # ;

        code.append("</varDec>")
        return code

    def compile_statements(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token

        if token in ["let", "if", "while", "do", "return"]:
            code = ["<statements>"]
            if token == "let":
                code += self.compile_let_statement(tokenizer)
            elif token == "if":
                code += self.compile_if_statement(tokenizer)
            elif token == "while":
                code += self.compile_while_statement(tokenizer)
            elif token == "do":
                code += self.compile_do_statement(tokenizer)
            else:
                code += self.compile_return_statement(tokenizer)

            while tokenizer.next_token()[0] in ["let", "if", "while", "do", "return"]:
                # we look ahead with statements to avoid advancing into a token beyond a statement
                token, token_type = tokenizer.advance()

                if token == "let":
                    code += self.compile_let_statement(tokenizer)
                elif token == "if":
                    code += self.compile_if_statement(tokenizer)
                elif token == "while":
                    code += self.compile_while_statement(tokenizer)
                elif token == "do":
                    code += self.compile_do_statement(tokenizer)
                else:
                    code += self.compile_return_statement(tokenizer)

            code.append("</statements>")
            return code
        else:
            return []

    def compile_let_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        assert (tokenizer.current_token[0] == "let")
        code = ["<letStatement>", terminal_xml_format("let", ELEMENTS["keyword"])]  # let
        token, token_type = tokenizer.advance()

        assert (token_type == ELEMENTS["identifier"])
        code.append(terminal_xml_format(token, token_type, "-".join(["", token,
                                                                     self.st.type_of(token),
                                                                     self.st.kind_of(token),
                                                                     str(self.st.index_of(token)),
                                                                     "assign"])))  # varName
        token, token_type = tokenizer.advance()

        # ([ expression ])?
        if token == "[":
            code.append(terminal_xml_format(token, token_type))  # [
            tokenizer.advance()

            code += self.compile_expression(tokenizer)
            token, token_type = tokenizer.advance()

            assert (token == "]")
            code.append(terminal_xml_format(token, token_type))  # ]
            token, token_type = tokenizer.advance()

        assert (token == "=")
        code.append(terminal_xml_format(token, token_type))  # =
        tokenizer.advance()

        code += self.compile_expression(tokenizer)
        token, token_type = tokenizer.advance()
        assert (token == ";")
        code.append(terminal_xml_format(token, token_type))  # ;

        code.append("</letStatement>")
        return code

    def compile_if_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        assert (tokenizer.current_token[0] == "if")
        code = ["<ifStatement>", terminal_xml_format("if", ELEMENTS["keyword"])]  # if
        token, token_type = tokenizer.advance()

        assert (token == "(")
        code.append(terminal_xml_format(token, token_type))  # (
        tokenizer.advance()

        code += self.compile_expression(tokenizer)
        token, token_type = tokenizer.advance()

        assert (token == ")")
        code.append(terminal_xml_format(token, token_type))  # )
        token, token_type = tokenizer.advance()

        assert (token == "{")
        code.append(terminal_xml_format(token, token_type))  # {
        token, token_type = tokenizer.advance()

        # statements
        if token in ["let", "if", "while", "do", "return"]:
            code += self.compile_statements(tokenizer)
            token, token_type = tokenizer.advance()

        assert (token == "}")
        code.append(terminal_xml_format(token, token_type))  # }

        if tokenizer.next_token()[0] == "else":
            token, token_type = tokenizer.advance()
            code.append(terminal_xml_format(token, token_type))  # else
            token, token_type = tokenizer.advance()

            assert (token == "{")
            code.append(terminal_xml_format(token, token_type))  # {
            token, token_type = tokenizer.advance()

            # statements
            if token in ["let", "if", "while", "do", "return"]:
                code += self.compile_statements(tokenizer)
                token, token_type = tokenizer.advance()

            assert (token == "}")
            code.append(terminal_xml_format(token, token_type))  # }

        code.append("</ifStatement>")
        return code

    def compile_while_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        assert (tokenizer.current_token[0] == "while")

        code = ["<whileStatement>", terminal_xml_format("while", ELEMENTS["keyword"])]  # while
        token, token_type = tokenizer.advance()

        assert (token == "(")
        code.append(terminal_xml_format(token, token_type))  # (
        tokenizer.advance()

        code += self.compile_expression(tokenizer)
        token, token_type = tokenizer.advance()

        assert (token == ")")
        code.append(terminal_xml_format(token, token_type))  # )
        token, token_type = tokenizer.advance()

        assert (token == "{")
        code.append(terminal_xml_format(token, token_type))  # {
        token, token_type = tokenizer.advance()

        # statements
        if token in ["let", "if", "while", "do", "return"]:
            code += self.compile_statements(tokenizer)
            token, token_type = tokenizer.advance()

        assert (token == "}")
        code.append(terminal_xml_format(token, token_type))  # }

        code.append("</whileStatement>")
        return code

    def compile_do_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        assert (tokenizer.current_token[0] == "do")
        code = ["<doStatement>", terminal_xml_format("do", ELEMENTS["keyword"])]  # do
        token, token_type = tokenizer.advance()

        # subroutineCall
        assert (token_type == ELEMENTS["identifier"])
        if tokenizer.next_token()[0] == ".":
            if self.st.kind_of(token) is not None:
                specification = "-".join(["", self.st.type_of(token),
                                          self.st.kind_of(token), str(self.st.index_of(token)), "use"])
            else:
                specification = "-classname-use"
        else:
            specification = "-subroutineName-use"
        code.append(terminal_xml_format(token, token_type, specification))  # subroutineName | (className | varName)
        token, token_type = tokenizer.advance()

        if token == ".":
            code.append(terminal_xml_format(token, token_type))  # .
            token, token_type = tokenizer.advance()

            assert (token_type == ELEMENTS["identifier"])
            code.append(terminal_xml_format(token, token_type, "subroutineName-use"))  # subroutineName
            token, token_type = tokenizer.advance()

        assert (token == "(")
        code.append(terminal_xml_format(token, token_type))  # (
        token, token_type = tokenizer.advance()

        if token != ")":
            code += self.compile_expression_list(tokenizer)  # expressionList
            token, token_type = tokenizer.advance()

        assert (token == ")")
        code.append(terminal_xml_format(token, token_type))  # )
        token, token_type = tokenizer.advance()
        # end of subroutine call

        assert (token == ";")
        code.append(terminal_xml_format(token, token_type))  # ;

        code.append("</doStatement>")
        return code

    def compile_return_statement(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        assert (tokenizer.current_token[0] == "return")
        code = ["<returnStatement>", terminal_xml_format("return", ELEMENTS["keyword"])]  # return
        token, token_type = tokenizer.advance()

        if token != ";":
            code += self.compile_expression(tokenizer)  # expression
            token, token_type = tokenizer.advance()

        assert (token == ";")
        code.append(terminal_xml_format(token, token_type))  # ;

        code.append("</returnStatement>")
        return code

    def compile_expression(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer

        code = ["<expression>"]
        code += self.compile_term(tokenizer)

        while tokenizer.next_token()[0] in OPS:
            token, token_type = tokenizer.advance()
            code.append(terminal_xml_format(token, token_type))  # op
            tokenizer.advance()
            code += self.compile_term(tokenizer)

        code.append("</expression>")
        return code

    def compile_term(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        code = ["<term>"]
        token, token_type = tokenizer.current_token

        # is it a simple term?
        if token_type in [ELEMENTS["integerConstant"], ELEMENTS["stringConstant"]] or token in KEYWORD_CONSTANTS:
            code.append(terminal_xml_format(token, token_type))  # simple term
        elif token in UNARY_OPS:
            code.append(terminal_xml_format(token, token_type))  # - or ~
            tokenizer.advance()
            code += self.compile_term(tokenizer)  # term
        elif token == "(":
            code.append(terminal_xml_format(token, token_type))  # (
            tokenizer.advance()

            code += self.compile_expression(tokenizer)  # expression
            token, token_type = tokenizer.advance()

            assert (token == ")")
            code.append(terminal_xml_format(token, token_type))  # )
        elif token_type == ELEMENTS["identifier"]:
            # could be varName | varName[expression] |
            # subroutineName(expressionList) | varName.subroutineName(expressionList)
            next_token = tokenizer.next_token()[0]
            if next_token == "[":
                code.append(terminal_xml_format(token, token_type, "-".join(["", self.st.type_of(token),
                                                                             self.st.kind_of(token),
                                                                             str(self.st.index_of(token)),
                                                                             "use"])))  # varName
                token, token_type = tokenizer.advance()

                code.append(terminal_xml_format(token, token_type))  # [
                tokenizer.advance()

                code += self.compile_expression(tokenizer)  # expression
                token, token_type = tokenizer.advance()

                assert (token == "]")
                code.append(terminal_xml_format(token, token_type))  # ]

            elif next_token == "(":
                # subroutineCall
                code.append(terminal_xml_format(token, token_type, "-subroutineName-use"))  # subroutineName
                token, token_type = tokenizer.advance()

                assert (token == "(")
                code.append(terminal_xml_format(token, token_type))  # (
                token, token_type = tokenizer.advance()

                if token != ")":
                    code += self.compile_expression_list(tokenizer)  # expressionList
                    token, token_type = tokenizer.advance()

                assert (token == ")")
                code.append(terminal_xml_format(token, token_type))  # )
                # end of subroutine call
            elif next_token == ".":
                if self.st.kind_of(token) is not None:
                    specification = "-".join(["", self.st.type_of(token),
                                              self.st.kind_of(token), str(self.st.index_of(token)), "use"])
                else:
                    specification = "-className-use"
                code.append(terminal_xml_format(token, token_type, specification))  # varName
                token, token_type = tokenizer.advance()

                code.append(terminal_xml_format(token, token_type))  # .
                tokenizer.advance()

                code += self.compile_term(tokenizer)  # subroutine(expressionList)
            else:
                code.append(terminal_xml_format(token, token_type, st=self.st))  # varName

        code.append("</term>")
        return code

    def compile_expression_list(self, tokenizer=None):
        tokenizer = tokenizer or self.tokenizer
        token, token_type = tokenizer.current_token
        code = ["<expressionList>"]
        if token != ")":

            code += self.compile_expression(tokenizer)

            while tokenizer.next_token()[0] == ",":
                token, token_type = tokenizer.advance()
                code.append(terminal_xml_format(token, token_type))  # ,
                tokenizer.advance()

                code += self.compile_expression(tokenizer)

        code.append("</expressionList>")
        return code


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
                    files_names.append(os.path.basename(file))

    elif file_or_dir.endswith(".jack"):
        input_files_paths = [file_or_dir]
        files_names.append(file_or_dir[:-5])
    else:
        print("Usage python JackAnalyzer filename.jack || python JackAnalyzer my_directory/ ")
        return

    # Parse input files one at a time
    for i, path in enumerate(input_files_paths):

        # generate token tree
        with open(files_names[i] + "T" + ".xml", "w") as token_tree:
            token_tree.write("<tokens>")
            tokenizer = JackTokenizer(path)
            while tokenizer.has_more_tokens():
                token, token_type = tokenizer.advance()
                token_tree.write(terminal_xml_format(token, token_type))

            token_tree.write("</tokens>")

        # generate parse tree
        with open(files_names[i] + ".xml", "w") as parse_tree:
            compiler = CompilationEngine(path)
            for code_line in compiler.compile_class():
                parse_tree.write(code_line)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage python JackAnalyzer filename.jack || python JackAnalyzer my_directory/ ")
        sys.exit(1)
    main(sys.argv[1])
