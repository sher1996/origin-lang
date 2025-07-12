# Debugger

The Origin debugger provides execution recording and replay capabilities to help debug your Origin programs.

## Execution Recording

### Basic Usage

To record the execution of your Origin program, use the `--record` flag:

```bash
origin run main.origin --record
```

This will:
1. Execute your program normally
2. Record each execution step to a `.orirec` file
3. Print the recording file path

### Recording File Format

The recording file (`.orirec`) contains JSONL (JSON Lines) format with one event per line:

```json
{"id": "LetNode:x", "ts": 1703123456.789, "env": {"variables": {"x": 5}, "functions": [], "node_type": "LetNode"}, "event_num": 0}
{"id": "SayNode:x", "ts": 1703123456.790, "env": {"variables": {"x": 5}, "functions": [], "node_type": "SayNode"}, "event_num": 1}
```

Each event contains:
- `id`: Unique identifier for the AST node
- `ts`: Timestamp when the event was recorded
- `env`: Environment snapshot (variables, functions, node type)
- `event_num`: Sequential event number

### File Naming

Recording files are automatically named with timestamps:
- `main-20241201-143022.orirec`
- `script-20241201-143045.orirec`

### Size Limits

To prevent recording files from growing too large:
- Each environment snapshot is capped at 64 KiB
- Large values are truncated with `<truncated>`
- Functions are recorded as names only (not bodies)

### Example

```origin
LET x = 5
LET y = 10
SAY x + y
```

Running with `--record`:
```bash
$ origin run example.origin --record
Recording to example-20241201-143022.orirec
15
```

The recording file will contain 3 events:
1. `LetNode:x` - sets x = 5
2. `LetNode:y` - sets y = 10  
3. `SayNode:x + y` - prints 15

## Performance

When `--record` is not used, there is **zero runtime overhead**. The recorder uses branch-predict-friendly checks:

```python
if self.recorder:
    self.recorder.record(node_id, env)
```

## Coming Soon: Replay

In Chapter 21, you'll be able to replay recorded executions:

```bash
origin debug example-20241201-143022.orirec
```

This will provide:
- Step-by-step execution replay
- Variable inspection at each step
- Breakpoint support
- Interactive debugging

## Advanced Usage

### Custom Recording Path

You can specify a custom recording directory:

```bash
origin run main.origin --record --output-dir /path/to/recordings
```

### Recording with Network Access

Record programs that use network features:

```bash
origin run network.origin --record --allow-net
```

### Recording with File Access

Record programs that read/write files:

```bash
origin run file_ops.origin --record --allow-files
```

## Troubleshooting

### Recording File Too Large

If your recording file is growing too large:
- Check for large variables or data structures
- Consider using smaller test data
- Large values will be automatically truncated

### Permission Errors

If you can't write the recording file:
- Check directory permissions
- Ensure disk space is available
- Try a different output directory

### Invalid Recording File

If the recording file is corrupted:
- Check for disk space issues
- Verify the program completed normally
- Re-run with `--record` to generate a new file 