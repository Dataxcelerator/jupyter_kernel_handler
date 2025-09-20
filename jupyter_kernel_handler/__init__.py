"""
Jupyter Kernel Handler - Cell Execution Monitor

This module provides colored output monitoring for Jupyter notebook cell execution.
Supports custom hooks for pre-run, real-time, and post-run events.

Usage:
    import jupyter_kernel_handler
    jupyter_kernel_handler.activate()
    # Optionally set custom hooks:
    jupyter_kernel_handler.set_hooks(pre_run=my_pre, realtime=my_real, post_run=my_post)
"""

import sys
import time
import threading
from IPython import get_ipython

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class CellOutputCapture:
    def __init__(self, debug_mode=False):
        self.original_stdout = None
        self.original_stderr = None
        self.captured_output = []
        self.is_capturing = False
        self.lock = threading.Lock()
        self.debug_mode = debug_mode

    def set_debug(self, debug):
        self.debug_mode = debug

    def start_capture(self):
        with self.lock:
            if not self.is_capturing:
                self.original_stdout = sys.stdout
                self.original_stderr = sys.stderr
                self.captured_output = []
                sys.stdout = self
                sys.stderr = self
                self.is_capturing = True

    def stop_capture(self):
        with self.lock:
            if self.is_capturing:
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
                self.is_capturing = False
                return ''.join(self.captured_output)
            return ''

    def write(self, text):
        if text and text.strip():
            with self.lock:
                self.captured_output.append(text)
                if self.original_stdout:
                    if self.debug_mode:
                        # Print line by line and wait for user input
                        for line in text.splitlines():
                            self.original_stdout.write(f"{Colors.GREEN}[DEBUG] {line}{Colors.END}\n")
                            self.original_stdout.flush()
                            input("Press Enter to continue...")
                    else:
                        self.original_stdout.write(f"{Colors.GREEN}[REALTIME] {text}{Colors.END}")
                        self.original_stdout.flush()

    def flush(self):
        if self.original_stdout:
            self.original_stdout.flush()


output_capture = CellOutputCapture()

def set_debug_mode(debug=True):
    output_capture.set_debug(debug)

# Default hooks
_user_pre_run = None
_user_realtime = None
_user_post_run = None

def default_pre_run(cell_content):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"🚀 PRE-RUN: Cell Content")
    print(f"{'='*60}{Colors.END}")
    lines = cell_content.strip().split('\n')
    for i, line in enumerate(lines, 1):
        print(f"{Colors.BLUE}[{i:2d}] {line}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}")
    print(f"⏱️  Execution starting...")
    print(f"{'='*60}{Colors.END}\n")

def default_realtime(text):
    if text and text.strip():
        timestamp = time.strftime("%H:%M:%S")
        print(f"{Colors.GREEN}[{timestamp}] {text.strip()}{Colors.END}")

def default_post_run(execution_result, execution_time, cell_content):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}{'='*60}")
    print(f"✅ POST-RUN: Execution Complete")
    print(f"{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}⏱️  Execution time: {execution_time:.3f} seconds{Colors.END}")
    print(f"{Colors.YELLOW}📝 Lines executed: {len(cell_content.strip().split(chr(10)))}{Colors.END}")
    if execution_result is not None:
        result_str = str(execution_result)
        if len(result_str) > 200:
            result_str = result_str[:200] + "..."
        print(f"{Colors.YELLOW}📊 Result type: {type(execution_result).__name__}{Colors.END}")
        if result_str.strip():
            print(f"{Colors.YELLOW}📋 Result preview: {result_str}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}📊 No return value{Colors.END}")
    print(f"{Colors.YELLOW}{'='*60}")
    print(f"🎉 Cell execution completed successfully!")
    print(f"{'='*60}{Colors.END}\n")

def set_hooks(pre_run=None, realtime=None, post_run=None):
    global _user_pre_run, _user_realtime, _user_post_run
    _user_pre_run = pre_run
    _user_realtime = realtime
    _user_post_run = post_run

def _call_hook(hook, default, *args):
    if hook:
        return hook(*args)
    else:
        return default(*args)



# --- Cell Content Capture Fix ---
import ast



class CellExecutionHook:
    def __init__(self):
        self.ip = get_ipython()
        self.active = False
        self._cell_content = 'No content available'
        self._allow_execution = True
        self.blocking_pre_run = False
        # Register AST transformer to capture cell source
        if self.ip is not None:
            self.ip.input_transformers_post.append(self._capture_cell_content)

    def _capture_cell_content(self, cell_source):
        self._cell_content = cell_source
        if hasattr(self.ip, 'user_ns'):
            self.ip.user_ns['_current_cell_content'] = cell_source
        return cell_source

    def pre_execute(self):
        if self.active and hasattr(self.ip, 'user_ns'):
            cell_content = getattr(self.ip.user_ns, '_current_cell_content', self._cell_content)
            # Reset flag before pre_run
            self._allow_execution = True
            # If blocking mode is enabled, allow pre_run to block execution
            result = _call_hook(_user_pre_run, default_pre_run, cell_content)
            if self.blocking_pre_run:
                if hasattr(self.ip, 'user_ns') and '_cell_allow_execution' in self.ip.user_ns:
                    self._allow_execution = self.ip.user_ns['_cell_allow_execution']
                if not self._allow_execution:
                    print(f"{Colors.RED}Cell execution blocked by pre_run hook.{Colors.END}")
                    raise RuntimeError("Cell execution blocked by pre_run hook.")
            output_capture.start_capture()
            self.ip.user_ns['_cell_start_time'] = time.time()

    def post_execute(self):
        if self.active:
            captured = output_capture.stop_capture()
            start_time = getattr(self.ip.user_ns, '_cell_start_time', time.time())
            execution_time = time.time() - start_time
            cell_content = getattr(self.ip.user_ns, '_current_cell_content', self._cell_content)
            result = getattr(self.ip.user_ns, '_', None)
            _call_hook(_user_post_run, default_post_run, result, execution_time, cell_content)

    def activate(self, debug_mode=False, blocking_pre_run=False):
        output_capture.set_debug(debug_mode)
        self.blocking_pre_run = blocking_pre_run
        if not self.active:
            self.ip.events.register('pre_execute', self.pre_execute)
            self.ip.events.register('post_execute', self.post_execute)
            self.active = True
            print(f"{Colors.PURPLE}🎯 Kernel Handler activated! All cell executions will now be monitored.{Colors.END}")

    def deactivate(self):
        if self.active:
            self.ip.events.unregister('pre_execute', self.pre_execute)
            self.ip.events.unregister('post_execute', self.post_execute)
            self.active = False
            print(f"{Colors.RED}🛑 Kernel Handler deactivated.{Colors.END}")

cell_hook = CellExecutionHook()

def activate(debug_mode=False, blocking_pre_run=False):
    cell_hook.activate(debug_mode=debug_mode, blocking_pre_run=blocking_pre_run)

def deactivate():
    cell_hook.deactivate()

def status():
    status = "ACTIVE" if cell_hook.active else "INACTIVE"
    color = Colors.GREEN if cell_hook.active else Colors.RED
    print(f"{color}Kernel Handler Status: {status}{Colors.END}")

if __name__ != '__main__':
    try:
        ip = get_ipython()
        if ip is not None:
            cell_hook.activate()
    except:
        print("Not running in IPython/Jupyter environment")

if __name__ == '__main__':
    print("Kernel Handler - Jupyter Notebook Execution Monitor")
    print("This module should be imported in a Jupyter notebook.")
    print("\nUsage:")
    print("  import jupyter_kernel_handler")
    print("  jupyter_kernel_handler.activate()")
    print("  jupyter_kernel_handler.set_hooks(pre_run, realtime, post_run)")
