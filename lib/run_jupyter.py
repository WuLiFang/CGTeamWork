# -*- coding=UTF-8 -*-
"""Run jupyter notebook.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import subprocess

from filetools import path


def main():
    exit(subprocess.call(
        [path('site-packages/bin/jupyter-notebook')],
        cwd=path('../notebook')))


if __name__ == '__main__':
    main()
