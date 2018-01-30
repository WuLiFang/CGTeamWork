# -*- coding=UTF-8 -*-
"""cgtwb module test.  """

from __future__ import absolute_import, unicode_literals, print_function
from unittest import TestCase, main


class CgtwbTestCase(TestCase):
    def setUp(self):
        from cgtwb import Current
        self.current = Current()

    def test_pipeline(self):
        print(self.current.pipeline)


if __name__ == '__main__':
    main()
