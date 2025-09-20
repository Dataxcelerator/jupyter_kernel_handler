from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='jupyter_kernel_handler',
    version='0.1.4',
    description='Jupyter Kernel Handler: Cell Execution Monitor with colored output and custom hooks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dataxcelerator',
    author_email='opensource@dataxcelerator.com',
    url='https://github.com/Dataxcelerator/jupyter_kernel_handler',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'ipython',
        'jupyter',
    ],
    python_requires='>=3.7',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
