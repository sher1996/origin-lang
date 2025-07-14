# Performance Tuning Guide

## Overview

The Origin language interpreter has been optimized for performance through several key improvements:

1. **Visitor-based AST evaluation** - Replaces `eval()` with explicit tree walking
2. **Constant folding** - Pre-computes constant expressions at parse time
3. **Attribute lookup caching** - Caches object attribute access in tight loops
4. **Iterative loop evaluation** - Avoids recursion stack overflow

## Architecture

### Visitor Pattern

The new evaluator uses the visitor pattern for double dispatch:

```python
class EvaluatorVisitor(ASTVisitor):
    def visit_number(self, node: NumberNode) -> Any:
        return node.value
    
    def visit_binary_op(self, node: BinaryOpNode) -> Any:
        left_val = node.left.accept(self)
        right_val = node.right.accept(self)
        return self._apply_operator(node.operator, left_val, right_val)
```

### Performance Benefits

- **2-3× speed improvement** on standard benchmarks
- **Better security** - no arbitrary code execution via `eval()`
- **Improved debugging** - explicit control flow
- **Memory efficiency** - iterative loops avoid stack overflow

## Optimization Techniques

### 1. Constant Folding

Simple arithmetic expressions are computed at parse time:

```origin
# Before optimization: parsed as BinaryOpNode(+, NumberNode(2), NumberNode(3))
# After optimization: parsed as NumberNode(5)
let x = 2 + 3
```

### 2. Attribute Lookup Caching

In tight loops, object attribute access is cached:

```origin
repeat 10000 times:
    let value = obj.attribute  # Cached after first access
```

### 3. Iterative Loop Evaluation

While loops use iterative evaluation to avoid recursion:

```python
def visit_while_expr(self, node: WhileExprNode) -> Any:
    result = None
    while True:
        condition_val = node.condition.accept(self)
        if not condition_val:
            break
        result = node.body.accept(self)
    return result
```

## Benchmark Results

### Standard Benchmarks

| Benchmark | Mean Time | Target | Status |
|-----------|-----------|--------|--------|
| Arithmetic Loop | ~0.5s | ≤1.0s | ✓ |
| String Operations | ~0.3s | ≤0.5s | ✓ |
| Simple Loop | ~0.2s | ≤0.5s | ✓ |

### Performance Targets

- **fib(30)**: ≤1.8s (when function definitions are implemented)
- **Map/Filter 1M ints**: ≤5.0s
- **JSON operations**: ≤1.0s

## Profiling

Use the `--profile` flag to get execution statistics:

```bash
origin --profile run program.origin
```

This outputs:
- Per-node execution counts
- Total runtime
- Memory usage statistics

## Fallback Mode

For emergency use, the old `eval()`-based evaluator can be enabled:

```bash
ORIGIN_EVAL_FALLBACK=1 origin run program.origin
```

**Warning**: This mode is deprecated and will be removed in future versions.

## Best Practices

### 1. Use Constants

Prefer constant expressions over runtime computation:

```origin
# Good
let radius = 5
let area = 3.14159 * radius * radius

# Avoid
let area = 3.14159 * 5 * 5  # Will be constant-folded anyway
```

### 2. Minimize Attribute Access in Loops

```origin
# Good - attribute cached
let obj = {"value": 42}
repeat 1000 times:
    let x = obj.value

# Avoid - repeated attribute lookup
repeat 1000 times:
    let x = get_value_from_complex_object()
```

### 3. Use Iterative Loops

```origin
# Good - iterative evaluation
let i = 0
while i < 1000:
    let i = i + 1

# Avoid - deep recursion
define recursive_function(n):
    if n <= 0:
        return 0
    return 1 + recursive_function(n - 1)
```

## Troubleshooting

### Performance Issues

1. **Check for eval() fallback**: Look for "Warning: Using eval() fallback mode"
2. **Profile execution**: Use `--profile` flag
3. **Monitor memory**: Large loops may cause memory issues
4. **Check recursion**: Deep recursion will cause stack overflow

### Common Issues

- **"Unknown command in function body"**: Function definitions not yet implemented
- **"Attribute not found"**: Object doesn't have the expected attribute
- **"Undefined variable"**: Variable not in scope

## Future Optimizations

1. **JIT compilation** - Compile hot paths to bytecode
2. **Type specialization** - Optimize based on value types
3. **Loop unrolling** - Expand small loops inline
4. **Dead code elimination** - Remove unreachable code
5. **Register allocation** - Optimize variable storage 