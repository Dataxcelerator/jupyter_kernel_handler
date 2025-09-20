"""
Jupyter Notebook Cell Execution Monitor

This module provides colored output monitoring for Jupyter notebook cell execution:
- pre_run_print: Shows cell content before execution (blue)
- realtime_print: Captures and displays output in real-time (green)
- post_run_print: Shows execution summary after completion (yellow)

Usage:
    In a Jupyter cell, run:
    %load_ext cell_monitor
    
    Or import and activate manually:
    import cell_monitor
    cell_monitor.activate()
"""

import sys
import io
import time
import threading
from contextlib import contextmanager
from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic
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
                # Real-time print with green color
                if self.original_stdout:
                    self.original_stdout.write(f"{Colors.GREEN}[REALTIME] {text}{Colors.END}")
                    self.original_stdout.flush()
    
    def flush(self):
        """Flush method for compatibility"""
        if self.original_stdout:
            self.original_stdout.flush()


# Global capture instance
output_capture = CellOutputCapture()


def pre_run_print(cell_content):
    """
    Print cell content before execution with blue color
    
    Args:
        cell_content (str): The content of the cell about to be executed
    """
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"🚀 PRE-RUN: Cell Content")
    print(f"{'='*60}{Colors.END}")
    
    # Clean and format cell content
    lines = cell_content.strip().split('\n')
    for i, line in enumerate(lines, 1):
        print(f"{Colors.BLUE}[{i:2d}] {line}{Colors.END}")
    
    print(f"{Colors.BLUE}{'='*60}")
    print(f"⏱️  Execution starting...")
    print(f"{'='*60}{Colors.END}\n")


def realtime_print(text):
    """
    Print output in real-time with green color
    
    Args:
        text (str): Text to print in real-time
    """
    if text and text.strip():
        timestamp = time.strftime("%H:%M:%S")
        print(f"{Colors.GREEN}[{timestamp}] {text.strip()}{Colors.END}")


def post_run_print(execution_result, execution_time, cell_content):
    """
    Print execution summary after cell completion with yellow color
    
    Args:
        execution_result: The result of the cell execution
        execution_time (float): Time taken for execution in seconds
        cell_content (str): The original cell content
    """
    print(f"\n{Colors.YELLOW}{Colors.BOLD}{'='*60}")
    print(f"✅ POST-RUN: Execution Complete")
    print(f"{'='*60}{Colors.END}")
    
    # Execution statistics
    print(f"{Colors.YELLOW}⏱️  Execution time: {execution_time:.3f} seconds{Colors.END}")
    print(f"{Colors.YELLOW}📝 Lines executed: {len(cell_content.strip().split(chr(10)))}{Colors.END}")
    
    # Result information
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
    """Manages the cell execution hooks"""
    
    def __init__(self):
        self.ip = get_ipython()
        self.active = False
    
    def pre_execute(self):
        """Called before cell execution"""
        if self.active and hasattr(self.ip, 'user_ns'):
            # Get the current cell content
            cell_content = getattr(self.ip, '_current_cell_content', 'No content available')
            pre_run_print(cell_content)
            
            # Start output capture for real-time monitoring
            output_capture.start_capture()
            
            # Store execution start time
            self.ip.user_ns['_cell_start_time'] = time.time()
    
    def post_execute(self):
        """Called after cell execution"""
        if self.active:
            # Stop output capture
            captured = output_capture.stop_capture()
            
            # Calculate execution time
            start_time = getattr(self.ip.user_ns, '_cell_start_time', time.time())
            execution_time = time.time() - start_time
            
            # Get cell content and result
            cell_content = getattr(self.ip, '_current_cell_content', 'No content available')
            result = getattr(self.ip.user_ns, '_', None)
            
            post_run_print(result, execution_time, cell_content)
    
    def activate(self):
        """Activate the cell execution hooks"""
        if not self.active:
            self.ip.events.register('pre_execute', self.pre_execute)
            self.ip.events.register('post_execute', self.post_execute)
            self.active = True
            print(f"{Colors.PURPLE}🎯 Cell Monitor activated! All cell executions will now be monitored.{Colors.END}")
    
    def deactivate(self):
        """Deactivate the cell execution hooks"""
        if self.active:
            self.ip.events.unregister('pre_execute', self.pre_execute)
            self.ip.events.unregister('post_execute', self.post_execute)
            self.active = False
            print(f"{Colors.RED}🛑 Cell Monitor deactivated.{Colors.END}")


# Global hook instance
cell_hook = CellExecutionHook()


@magics_class
class CellMonitorMagics(Magics):
    """Magic commands for controlling cell monitoring"""
    
    @line_magic
    def cell_monitor_on(self, line):
        """Turn on cell monitoring"""
        cell_hook.activate()
    
    @line_magic
    def cell_monitor_off(self, line):
        """Turn off cell monitoring"""
        cell_hook.deactivate()
    
    @line_magic
    def cell_monitor_status(self, line):
        """Show cell monitoring status"""
        status = "ACTIVE" if cell_hook.active else "INACTIVE"
        color = Colors.GREEN if cell_hook.active else Colors.RED
        print(f"{color}Cell Monitor Status: {status}{Colors.END}")


def load_ipython_extension(ipython):
    """Load the extension when %load_ext is used"""
    # Store cell content before execution
    def store_cell_content(lines):
        ipython._current_cell_content = '\n'.join(lines)
    
    # Hook into the input transformer to capture cell content
    original_transform = ipython.input_transformer_manager.transform_cell
    
    def enhanced_transform(raw_cell):
        ipython._current_cell_content = raw_cell
        return original_transform(raw_cell)
    
    ipython.input_transformer_manager.transform_cell = enhanced_transform
    
    # Register magic commands
    ipython.register_magic_function(CellMonitorMagics(ipython).cell_monitor_on, 'line', 'cell_monitor_on')
    ipython.register_magic_function(CellMonitorMagics(ipython).cell_monitor_off, 'line', 'cell_monitor_off')
    ipython.register_magic_function(CellMonitorMagics(ipython).cell_monitor_status, 'line', 'cell_monitor_status')
    
    # Auto-activate monitoring
    cell_hook.activate()


def unload_ipython_extension(ipython):
    """Unload the extension"""
    cell_hook.deactivate()


# Convenience functions for manual activation
def activate():
    """Manually activate cell monitoring"""
    cell_hook.activate()


def deactivate():
    """Manually deactivate cell monitoring"""
    cell_hook.deactivate()


def status():
    """Show monitoring status"""
    status = "ACTIVE" if cell_hook.active else "INACTIVE"
    color = Colors.GREEN if cell_hook.active else Colors.RED
    print(f"{color}Cell Monitor Status: {status}{Colors.END}")


# Auto-load if imported directly
if __name__ != '__main__':
    try:
        ip = get_ipython()
        if ip is not None:
            load_ipython_extension(ip)
    except:
        print("Not running in IPython/Jupyter environment")


if __name__ == '__main__':
    print("Cell Monitor - Jupyter Notebook Execution Monitor")
    print("This module should be imported in a Jupyter notebook or loaded as an extension.")
    print("\nUsage:")
    print("  %load_ext cell_monitor")
    print("  or")
    print("  import cell_monitor")
    print("  cell_monitor.activate()")
