import lexer
import parser

# Test the error demo content
source = 'foo "bar"'
print(f"Source: {source}")

tokens = lexer.tokenize(source)
print(f"Tokens: {tokens}")

ast = parser.parse(tokens)
print(f"AST: {ast}")

# Try to execute
import runtime
try:
    runtime.execute(ast)
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")

# Write to file for debugging
with open('debug_output.txt', 'w') as f:
    f.write(f"Source: {source}\n")
    f.write(f"Tokens: {tokens}\n")
    f.write(f"AST: {ast}\n")
    try:
        runtime.execute(ast)
    except Exception as e:
        f.write(f"Error: {e}\n")
        f.write(f"Error type: {type(e)}\n") 