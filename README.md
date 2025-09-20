# Jupyter Kernel Handler

Jupyter Kernel Handler: Cell Execution Monitor with colored output and custom hooks for Jupyter notebooks.

GitHub: https://github.com/Dataxcelerator/jupyter_kernel_handler

## Features
- Pre-run cell content display (blue)
- Real-time output (green)
- Post-run summary (yellow)
- Custom hooks for pre-run, real-time, and post-run events

## Usage
```python
import jupyter_kernel_handler
jupyter_kernel_handler.activate()
# Optionally set custom hooks:
jupyter_kernel_handler.set_hooks(pre_run=my_pre, realtime=my_real, post_run=my_post)
```

## License
MIT
