# -*- coding=UTF-8 -*-
"""Run aia manager.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

if __name__ == '__main__':
    import localsite
    localsite.setup()
    import aia_status_transfer
    aia_status_transfer.main()
