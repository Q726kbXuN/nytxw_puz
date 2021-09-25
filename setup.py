#!/usr/bin/env python3

from distutils.core import setup
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
    zipfile=None,
)
