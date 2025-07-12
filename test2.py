import lexer
from runtime import replace_plus_outside_strings
expr = '"Debug: " + n'
print(replace_plus_outside_strings(expr)) 