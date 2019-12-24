# -*- coding=UTF-8 -*-
"""Cgteamwork uploader entry. """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import cgtwq_uploader

import cgtwq.helper.wlf


def setup_prefix_filter():
    """Add custom prefix filter for wrong naming.  """

    cgtwq.helper.wlf.CGTWQHelper.prefix_filters.append(
        lambda x: x.replace('XJCG', 'XJ'))
    cgtwq.helper.wlf.CGTWQHelper.prefix_filters.append(
        lambda x: x.replace('QNPV', 'QNYH'))


if __name__ == '__main__':
    setup_prefix_filter()
    cgtwq_uploader.main()
