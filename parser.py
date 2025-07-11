from typing import List, Any

class Node:
    pass

class SayNode(Node):
    def __init__(self, expr):
        self.expr = expr

class LetNode(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class RepeatNode(Node):
    def __init__(self, count, body):
        self.count = count
        self.body = body

class FuncDefNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FuncCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ExprStmtNode(Node):
    def __init__(self, expr):
        self.expr = expr

class ExprNode(Node):
    def __init__(self, expr):
        self.expr = expr

# Minimal parser for the current language
class Parser:
    def __init__(self, tokens: List[Any]):
        self.tokens = tokens
        self.pos = 0
        self.length = len(tokens)

    def peek(self, offset=0):
        if self.pos + offset < self.length:
            return self.tokens[self.pos + offset]
        return None

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.pos < self.length:
            tok = self.peek()
            if tok and tok[0] == 'LET':
                self.advance()  # LET
                name_tok = self.advance()
                name = name_tok[1] if name_tok else None
                self.advance()  # EQUALS
                expr_tok = self.advance()
                expr = expr_tok[1] if expr_tok else None
                stmts.append(LetNode(name, expr))
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
            elif tok and tok[0] == 'SAY':
                self.advance()  # SAY
                expr_tok = self.advance()
                expr = expr_tok[1] if expr_tok else None
                stmts.append(SayNode(expr))
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
            elif tok and tok[0] == 'REPEAT':
                self.advance()  # REPEAT
                count_tok = self.advance()
                count = count_tok[1] if count_tok else None
                self.advance()  # TIMES
                self.advance()  # COLON
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
                body = []
                next_tok = self.peek()
                if next_tok and next_tok[0] == 'INDENT':
                    self.advance()
                    while True:
                        inner_tok = self.peek()
                        if not inner_tok or inner_tok[0] == 'DEDENT':
                            break
                        if inner_tok[0] == 'LET':
                            self.advance()
                            name_tok = self.advance()
                            name = name_tok[1] if name_tok else None
                            self.advance()
                            expr_tok = self.advance()
                            expr = expr_tok[1] if expr_tok else None
                            body.append(LetNode(name, expr))
                            if self.peek() and self.peek()[0] == 'NEWLINE':
                                self.advance()
                        elif inner_tok[0] == 'SAY':
                            self.advance()
                            expr_tok = self.advance()
                            expr = expr_tok[1] if expr_tok else None
                            body.append(SayNode(expr))
                            if self.peek() and self.peek()[0] == 'NEWLINE':
                                self.advance()
                        else:
                            raise SyntaxError(f"Unknown command in repeat body: {inner_tok}")
                    if self.peek() and self.peek()[0] == 'DEDENT':
                        self.advance()
                stmts.append(RepeatNode(count, body))
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
            elif tok and tok[0] == 'DEFINE':
                self.advance()  # DEFINE
                name_tok = self.advance()
                name = name_tok[1] if name_tok else None
                self.advance()  # LPAREN
                params = []
                while self.peek() and self.peek()[0] == 'IDENT':
                    param_tok = self.advance()
                    if param_tok:
                        params.append(param_tok[1])
                    if self.peek() and self.peek()[0] == 'COMMA':
                        self.advance()  # COMMA
                self.advance()  # RPAREN
                self.advance()  # COLON
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
                body = []
                next_tok = self.peek()
                if next_tok and next_tok[0] == 'INDENT':
                    self.advance()
                    while True:
                        inner_tok = self.peek()
                        if not inner_tok or inner_tok[0] == 'DEDENT':
                            break
                        if inner_tok[0] == 'LET':
                            self.advance()
                            name_tok = self.advance()
                            func_name = name_tok[1] if name_tok else None
                            self.advance()
                            expr_tok = self.advance()
                            expr = expr_tok[1] if expr_tok else None
                            body.append(LetNode(func_name, expr))
                            if self.peek() and self.peek()[0] == 'NEWLINE':
                                self.advance()
                        elif inner_tok[0] == 'SAY':
                            self.advance()
                            expr_tok = self.advance()
                            expr = expr_tok[1] if expr_tok else None
                            body.append(SayNode(expr))
                            if self.peek() and self.peek()[0] == 'NEWLINE':
                                self.advance()
                        elif inner_tok[0] == 'EXPR':
                            self.advance()
                            expr = inner_tok[1]
                            body.append(ExprStmtNode(expr))
                            if self.peek() and self.peek()[0] == 'NEWLINE':
                                self.advance()
                        else:
                            raise SyntaxError(f"Unknown command in function body: {inner_tok}")
                    if self.peek() and self.peek()[0] == 'DEDENT':
                        self.advance()
                stmts.append(FuncDefNode(name, params, body))
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
            elif tok and tok[0] == 'IDENT' and self.peek(1) and self.peek(1)[0] == 'LPAREN':
                # Function call
                name_tok = self.advance()
                func_name = name_tok[1] if name_tok else None
                self.advance()  # LPAREN
                args = []
                while self.peek() and self.peek()[0] == 'EXPR':
                    arg_tok = self.advance()
                    if arg_tok:
                        args.append(arg_tok[1])
                    if self.peek() and self.peek()[0] == 'COMMA':
                        self.advance()  # COMMA
                self.advance()  # RPAREN
                stmts.append(FuncCallNode(func_name, args))
                if self.peek() and self.peek()[0] == 'NEWLINE':
                    self.advance()
            elif tok and tok[0] in ('NEWLINE', 'DEDENT'):
                self.advance()
            else:
                self.advance()
        return stmts

def parse(tokens: List[Any]):
    return Parser(tokens).parse() 