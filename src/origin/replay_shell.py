import sys
from typing import Optional

from .replayer import Replayer
from .diff import compute_diff, format_diff

class ReplayShell:
    """Interactive shell for replaying recorded execution events."""
    
    def __init__(self, replayer: Replayer):
        """Initialize the replay shell with a replayer."""
        self.replayer = replayer
        self.previous_env: Optional[dict] = None
    
    def display_current_state(self) -> None:
        """Display current event information and changes."""
        event = self.replayer.current_event()
        if not event:
            print("No current event")
            return
        
        info = self.replayer.get_info()
        print(f"\n[{info['current_index'] + 1}/{info['total_events']}] {event['id']}")
        
        # Show changes if we have a previous environment
        if self.previous_env is not None:
            current_env = self.replayer.current_env()
            if current_env:
                changes = compute_diff(self.previous_env, current_env)
                if changes:
                    print("Changes:")
                    print(format_diff(changes))
                else:
                    print("No changes")
        
        # Update previous environment for next comparison
        self.previous_env = self.replayer.current_env()
    
    def show_help(self) -> None:
        """Display help information."""
        print("\nCommands:")
        print("  (r)un     - Run through all remaining events")
        print("  (n)ext    - Go to next event")
        print("  (p)rev    - Go to previous event")
        print("  (g)o <k>  - Jump to event k (0-based)")
        print("  (q)uit    - Exit replay")
        print("  (h)elp    - Show this help")
    
    def handle_goto(self, args: str) -> bool:
        """Handle goto command with index."""
        try:
            index = int(args.strip())
            event = self.replayer.goto(index)
            if event:
                return True
            else:
                print(f"Invalid index: {index}")
                return False
        except ValueError:
            print("Invalid index. Use: g <number>")
            return False
    
    def run(self) -> None:
        """Run the interactive replay shell."""
        print("Origin Replay Shell")
        print("Type 'h' for help")
        
        # Start at first event
        if self.replayer.next():
            self.display_current_state()
        
        while True:
            try:
                command = input("\n(r)un (n)ext (p)rev (g)o <k> (q)uit: ").strip().lower()
                
                if not command:
                    continue
                
                if command in ['q', 'quit']:
                    print("Goodbye!")
                    break
                
                elif command in ['h', 'help']:
                    self.show_help()
                
                elif command in ['n', 'next']:
                    if self.replayer.next():
                        self.display_current_state()
                    else:
                        print("Already at last event")
                
                elif command in ['p', 'prev']:
                    if self.replayer.prev():
                        self.display_current_state()
                    else:
                        print("Already at first event")
                
                elif command in ['r', 'run']:
                    print("Running through remaining events...")
                    self.replayer.run()
                    print("Finished!")
                    # Show final state
                    self.display_current_state()
                
                elif command.startswith('g '):
                    if self.handle_goto(command[2:]):
                        self.display_current_state()
                
                elif command.startswith('go '):
                    if self.handle_goto(command[3:]):
                        self.display_current_state()
                
                else:
                    print("Unknown command. Type 'h' for help.")
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}") 