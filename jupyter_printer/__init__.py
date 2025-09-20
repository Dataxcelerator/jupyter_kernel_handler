"""
Jupyter Notebook Cell Execution Monitor

This module provides colored output monitoring for Jupyter notebook cell execution:
- pre_run_print: Shows cell content before execution (blue)
- realtime_print: Captures and displays output in real-time (green)
- post_run_print: Shows execution summary after completion (yellow)

Usage:
    In a Jupyter cell, run:
    import jupyter_printer
    jupyter_printer.activate()
"""

import sys
import io
import time
import threading
from contextlib import contextmanager
from IPython import get_ipython
from IPython.core.events import EventManager
from IPython.display import display, HTML
import re

class Colors:
    """ANSI color codes for terminal output"""
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
    """Captures and manages cell output in real-time"""
    def __init__(self):
        self.original_stdout = None
        self.original_stderr = None
        self.captured_output = []
        self.is_capturing = False
        self.lock = threading.Lock()
    def start_capture(self):
        """Start capturing stdout and stderr"""
        with self.lock:
            if not self.is_capturing:
                self.original_stdout = sys.stdout
                self.original_stderr = sys.stderr
                self.captured_output = []
                sys.stdout = self
                sys.stderr = self
                self.is_capturing = True
    def stop_capture(self):
        """Stop capturing and restore original streams"""
        with self.lock:
            if self.is_capturing:
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
                self.is_capturing = False
                return ''.join(self.captured_output)
            return ''
    def write(self, text):
        """Write method for stdout/stderr capture"""
        if text and text.strip():
            with self.lock:
                self.captured_output.append(text)
                if self.original_stdout:
                    self.original_stdout.write(f"{Colors.GREEN}[REALTIME] {text}{Colors.END}")
                    self.original_stdout.flush()
    def flush(self):
        """Flush method for compatibility"""
        if self.original_stdout:
            self.original_stdout.flush()

output_capture = CellOutputCapture()

def pre_run_print(cell_content):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"🚀 PRE-RUN: Cell Content")
    print(f"{'='*60}{Colors.END}")
    lines = cell_content.strip().split('\n')
    for i, line in enumerate(lines, 1):
        print(f"{Colors.BLUE}[{i:2d}] {line}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}")
    print(f"⏱️  Execution starting...")
    print(f"{'='*60}{Colors.END}\n")

def realtime_print(text):
    if text and text.strip():
        timestamp = time.strftime("%H:%M:%S")
        print(f"{Colors.GREEN}[{timestamp}] {text.strip()}{Colors.END}")

def post_run_print(execution_result, execution_time, cell_content):
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

class CellExecutionHook:
    def __init__(self):
        self.ip = get_ipython()
        self.active = False
    def pre_execute(self):
        if self.active and hasattr(self.ip, 'user_ns'):
            cell_content = getattr(self.ip, '_current_cell_content', 'No content available')
            pre_run_print(cell_content)
            output_capture.start_capture()
            self.ip.user_ns['_cell_start_time'] = time.time()
    def post_execute(self):
        if self.active:
            captured = output_capture.stop_capture()
            start_time = getattr(self.ip.user_ns, '_cell_start_time', time.time())
            execution_time = time.time() - start_time
            cell_content = getattr(self.ip, '_current_cell_content', 'No content available')
            result = getattr(self.ip.user_ns, '_', None)
            post_run_print(result, execution_time, cell_content)
    def activate(self):
        if not self.active:
            self.ip.events.register('pre_execute', self.pre_execute)
            self.ip.events.register('post_execute', self.post_execute)
            self.active = True
            print(f"{Colors.PURPLE}🎯 Cell Monitor activated! All cell executions will now be monitored.{Colors.END}")
    def deactivate(self):
        if self.active:
            self.ip.events.unregister('pre_execute', self.pre_execute)
            self.ip.events.unregister('post_execute', self.post_execute)
            self.active = False
            print(f"{Colors.RED}🛑 Cell Monitor deactivated.{Colors.END}")

cell_hook = CellExecutionHook()

def activate():
    cell_hook.activate()

def deactivate():
    cell_hook.deactivate()

def status():
    status = "ACTIVE" if cell_hook.active else "INACTIVE"
    color = Colors.GREEN if cell_hook.active else Colors.RED
    print(f"{color}Cell Monitor Status: {status}{Colors.END}")

if __name__ != '__main__':
    try:
        ip = get_ipython()
        if ip is not None:
            cell_hook.activate()
    except:
        print("Not running in IPython/Jupyter environment")

if __name__ == '__main__':
    print("Cell Monitor - Jupyter Notebook Execution Monitor")
    print("This module should be imported in a Jupyter notebook or loaded as an extension.")
    print("\nUsage:")
    print("  import jupyter_printer")
    print("  jupyter_printer.activate()")
