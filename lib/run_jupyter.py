# -*- coding=UTF-8 -*-
"""Run jupyter notebook.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import subprocess

from filetools import path


def main():
    env = dict(os.environ)
    env[b'LANG'] = b'en_US'
    exit(subprocess.call(
        [path('site-packages/bin/jupyter-notebook')],
        cwd=path('../notebook'), env=env))


if __name__ == '__main__':
    main()
