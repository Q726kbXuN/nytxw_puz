#!/usr/bin/env python3

from distutils.core import setup
from setuptools import find_packages
import py2exe

py2exe.freeze(
    console=[{
        'script': 'nyt.py',
        'dest_base': 'nytxw_puz',
        'product_name': 'nytxw_puz',
    }],
    options={
        'py2exe': {
            'bundle_files': 1,
            'dist_dir': 'dist',
        }
    },
    zipfile=None,
)
