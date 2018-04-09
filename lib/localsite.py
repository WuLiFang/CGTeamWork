# -*- coding=UTF-8
"""Local site for share on server.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import site
import sys
import filetools


def setup():
    dir_ = filetools.path('site-packages')
    sys.path.insert(0, dir_)
    site.addsitedir(dir_)
