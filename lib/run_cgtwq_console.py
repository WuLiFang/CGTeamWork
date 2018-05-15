# -*- coding=UTF-8 -*-
"""Cgtwq console entry. """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

if __name__ == '__main__':
    import localsite
    localsite.setup()
    import cgtwq_console
    cgtwq_console.main()
