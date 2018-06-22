# -*- coding=UTF-8 -*-
"""Cgteamwork uploader entry. """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def setup_prefix_filter():
    """Add custom prefix filter for wrong naming.  """

    import cgtwq.helper.wlf
    cgtwq.helper.wlf.CGTWQHelper.prefix_filters.append(
        lambda x: x.replace('XJCG', 'XJ'))


if __name__ == '__main__':
    import localsite
    localsite.setup()
    setup_prefix_filter()
    import cgtwq_uploader
    cgtwq_uploader.main()
