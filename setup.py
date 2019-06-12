import os
from setuptools import setup, find_packages

setup(
    name='rubens',
    version="1.0.0",
    author='Ruben Vereecken',
    entry_points={
        'console_scripts': [
            'inspect-experiment-id = rubens.scripts.inspect_name:main',
        ]
    }
)

