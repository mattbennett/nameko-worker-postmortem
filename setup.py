#!/usr/bin/env python
import os
from codecs import open

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), 'r', 'utf-8') as handle:
    readme = handle.read()


setup(
    name='nameko_worker_postmortem',
    version='1.0.0',
    description='Drop into PDB post mortem on Nameko worker exceptions',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='mattbennett',
    url='http://github.com/mattbennett/nameko-worker-postmortem',
    py_modules=['nameko_worker_postmortem'],
    install_requires=[
        "nameko",
        "pytest"
    ],
    extras_require={
        'dev': [
            "coverage==4.4.1"
        ]
    },
    entry_points={
        'pytest11': [
            'nameko_worker_postmortem=nameko_worker_postmortem'
        ]
    },
    zip_safe=True,
    license='Apache License, Version 2.0',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
