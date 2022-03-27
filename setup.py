#!/usr/bin/env python3

from distutils.core import setup
from setuptools import find_packages
import py2exe


setup(
    name='nytxw_puz',
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
    packages=find_packages(
        where='src',
        exclude=['other', 'images'],
    ),
    zipfile=None,
)
