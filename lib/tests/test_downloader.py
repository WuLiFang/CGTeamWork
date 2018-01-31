# -*- coding=UTF-8 -*-
"""Cgtw downloader test.  """

from __future__ import absolute_import, print_function, unicode_literals

from unittest import TestCase, main, skipUnless

from wlf.cgtwq import MODULE_ENABLE, CGTeamWork


@skipUnless(MODULE_ENABLE and CGTeamWork.update_status(), 'Need server to test.')
class ServerFilesTestCase(TestCase):
    def test_update(self):
        from downloader import ServerFiles
        for target in ('Final', 'Submit'):
            print(ServerFiles(target))


if __name__ == '__main__':
    main()
