# -*- coding=UTF-8 -*-
"""Cgtw downloader test.  """

from __future__ import absolute_import, unicode_literals, print_function
from unittest import TestCase, main


class ServerFilesTestCase(TestCase):
    def test_update(self):
        from downloader import ServerFiles
        for target in ('Final', 'Submit'):
            print(ServerFiles(target))


if __name__ == '__main__':
    main()
