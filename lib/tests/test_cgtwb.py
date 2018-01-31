# -*- coding=UTF-8 -*-
"""cgtwb module test.  """

from __future__ import absolute_import, print_function, unicode_literals

from unittest import TestCase, main, skipUnless

from wlf.cgtwq import MODULE_ENABLE, CGTeamWork


@skipUnless(MODULE_ENABLE and CGTeamWork.update_status(), 'Need server to test.')
class CgtwbTestCase(TestCase):

    def setUp(self):

        from cgtwb import Current
        self.current = Current()

    def test_pipeline(self):
        print(self.current.pipeline)


if __name__ == '__main__':
    main()
