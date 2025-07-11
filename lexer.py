import re
from typing import List, Tuple, Union

Token = Tuple[str, Union[str, int, float]]

def tokenize(source: str) -> List[Token]:
    tokens = []
    lines = source.splitlines()
    indent_stack = [0]
    for lineno, raw in enumerate(lines):
        line = raw.split('#', 1)[0].rstrip('\n')
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(' '))
        if indent > indent_stack[-1]:
            tokens.append(('INDENT', None))
            indent_stack.append(indent)
        while indent < indent_stack[-1]:
            tokens.append(('DEDENT', None))
            indent_stack.pop()
        stripped = line.strip()
        if stripped.startswith('let '):
            tokens.append(('LET', 'let'))
            rest = stripped[4:].strip()
            name, expr = map(str.strip, rest.split('=', 1))
            tokens.append(('IDENT', name))
            tokens.append(('EQUALS', '='))
            tokens.append(('EXPR', expr))
        elif stripped.startswith('say '):
            tokens.append(('SAY', 'say'))
            expr = stripped[4:].strip()
            tokens.append(('EXPR', expr))
        elif stripped.startswith('repeat ') and stripped.endswith(' times:'):
            m = re.match(r'repeat (\d+) times:', stripped)
            if not m:
                raise SyntaxError(f"Invalid repeat syntax: {stripped}")
            tokens.append(('REPEAT', 'repeat'))
            tokens.append(('NUMBER', int(m.group(1))))
            tokens.append(('TIMES', 'times'))
            tokens.append(('COLON', ':'))
        elif stripped.startswith('define '):
            tokens.append(('DEFINE', 'define'))
            rest = stripped[7:].strip()
            if ':' not in rest:
                raise SyntaxError(f"Invalid function definition: {stripped}")
            func_part, _ = rest.split(':', 1)
            func_part = func_part.strip()
            if '(' in func_part and func_part.endswith(')'):
                name = func_part[:func_part.find('(')].strip()
                params_part = func_part[func_part.find('(')+1:func_part.rfind(')')].strip()
                tokens.append(('IDENT', name))
                tokens.append(('LPAREN', '('))
                if params_part:
                    params = [p.strip() for p in params_part.split(',')]
                    for i, param in enumerate(params):
                        tokens.append(('IDENT', param))
                        if i < len(params) - 1:
                            tokens.append(('COMMA', ','))
                tokens.append(('RPAREN', ')'))
                tokens.append(('COLON', ':'))
            else:
                raise SyntaxError(f"Invalid function definition: {stripped}")
        elif '(' in stripped and ')' in stripped:
            # Function call
            name = stripped[:stripped.find('(')].strip()
            args_part = stripped[stripped.find('(')+1:stripped.rfind(')')].strip()
            tokens.append(('IDENT', name))
            tokens.append(('LPAREN', '('))
            if args_part:
                args = [arg.strip() for arg in args_part.split(',')]
                for i, arg in enumerate(args):
                    tokens.append(('EXPR', arg))
                    if i < len(args) - 1:
                        tokens.append(('COMMA', ','))
            tokens.append(('RPAREN', ')'))
        else:
            # Standalone expression (for function return values)
            tokens.append(('EXPR', stripped))
        tokens.append(('NEWLINE', None))
    while len(indent_stack) > 1:
        tokens.append(('DEDENT', None))
        indent_stack.pop()
    return tokens 