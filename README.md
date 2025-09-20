
# Jupyter Kernel Handler

Cell Execution Monitor with colored output and custom hooks for Jupyter notebooks.

## Features
- Pre-run cell content display (blue)
- Real-time output (green)
- Post-run summary (yellow)
- Custom hooks for pre-run, real-time, and post-run events
- Debug mode for line-by-line real-time output


## Installation

### From PyPI (public release)
```bash
pip install jupyter_kernel_handler
```

### From GitHub (latest code)
```bash
pip install git+https://github.com/Dataxcelerator/jupyter_kernel_handler.git
```


### Secure PyPI Publishing with .env
For publishing to PyPI, store your API key in a `.env` file:
```env
PIPY_API_KEY=pypi-xxxxxx
```
This file is automatically ignored by git for security.

To upload your package:
```bash
export $(cat .env | xargs)
python3 -m twine upload -u __token__ -p $PIPY_API_KEY dist/*
```

For private installs:
```bash
pip install --extra-index-url https://__token__:$PIPY_API_KEY@pypi.org/simple jupyter_kernel_handler
```

## Usage
```python
import jupyter_kernel_handler
jupyter_kernel_handler.set_hooks(pre_run=my_pre, realtime=my_real, post_run=my_post)
jupyter_kernel_handler.activate(debug_mode=True)
```

## Changelog
See `CHANGELOG.md` for recent updates and improvements.

See the notebook `run.ipynb` for a full demo.

## License
MIT

## Source
[GitHub Repository](https://github.com/Dataxcelerator/jupyter_kernel_handler.git)
