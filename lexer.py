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
        else:
            raise SyntaxError(f"Unknown command: {stripped}")
        tokens.append(('NEWLINE', None))
    while len(indent_stack) > 1:
        tokens.append(('DEDENT', None))
        indent_stack.pop()
    return tokens 