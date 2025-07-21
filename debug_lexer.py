import lexer

# Test with a simpler, correctly formatted Origin program
origin_code = '''let x = 5
say x'''

print("Input code:")
print(repr(origin_code))
print()

try:
    tokens = lexer.tokenize(origin_code)
    print("Tokens:")
    for i, token in enumerate(tokens):
        print(f"{i}: {token}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 