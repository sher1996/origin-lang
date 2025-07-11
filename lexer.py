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
        
        # Handle string literals first
        if stripped.startswith('"') and stripped.count('"') >= 2:
            # Find the closing quote
            end_quote = stripped.find('"', 1)
            if end_quote != -1:
                string_content = stripped[1:end_quote]
                tokens.append(('STRING', string_content))
                remaining = stripped[end_quote + 1:].strip()
                if remaining:
                    # Process remaining content
                    if remaining.startswith('import '):
                        m = re.match(r'import\s+"([^"]+)"', remaining)
                        if not m:
                            raise SyntaxError(f"Invalid import syntax: {remaining}")
                        tokens.append(('IMPORT', m.group(1)))
                        tokens.append(('NEWLINE', None))
                        continue
                    if remaining.startswith('let '):
                        tokens.append(('LET', 'let'))
                        rest = remaining[4:].strip()
                        name, expr = map(str.strip, rest.split('=', 1))
                        tokens.append(('IDENT', name))
                        tokens.append(('EQUALS', '='))
                        tokens.append(('EXPR', expr))
                    elif remaining.startswith('say '):
                        tokens.append(('SAY', 'say'))
                        expr = remaining[4:].strip()
                        tokens.append(('EXPR', expr))
                    elif remaining.startswith('repeat ') and remaining.endswith(' times:'):
                        m = re.match(r'repeat (\d+) times:', remaining)
                        if not m:
                            raise SyntaxError(f"Invalid repeat syntax: {remaining}")
                        tokens.append(('REPEAT', 'repeat'))
                        tokens.append(('NUMBER', int(m.group(1))))
                        tokens.append(('TIMES', 'times'))
                        tokens.append(('COLON', ':'))
                    elif remaining.startswith('define '):
                        tokens.append(('DEFINE', 'define'))
                        rest = remaining[7:].strip()
                        if ':' not in rest:
                            raise SyntaxError(f"Invalid function definition: {remaining}")
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
                            raise SyntaxError(f"Invalid function definition: {remaining}")
                    elif '(' in remaining and ')' in remaining:
                        # Function call
                        name = remaining[:remaining.find('(')].strip()
                        args_part = remaining[remaining.find('(')+1:remaining.rfind(')')].strip()
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
                        tokens.append(('EXPR', remaining))
                tokens.append(('NEWLINE', None))
                continue
        
        if stripped.startswith('import '):
            m = re.match(r'import\s+"([^"]+)"', stripped)
            if not m:
                raise SyntaxError(f"Invalid import syntax: {stripped}")
            tokens.append(('IMPORT', m.group(1)))
            tokens.append(('NEWLINE', None))
            continue
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