#!/usr/bin/env python3

import os

if os.name == 'nt':
    from distutils.core import setup
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
else:
    raise Exception()
