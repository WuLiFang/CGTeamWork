# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from wlf.pathtools import make_path_finder
from Qt.QtWidgets import QFileDialog

from typing import Text
from wlf.uitools import application
path = make_path_finder(__file__)  # pylint: disable=invalid-name


def ask_filename():
    # type: () -> Text
    """Ask user for filename.  """
    dummy = application()
    filename, _ = QFileDialog.getOpenFileName(
        None, caption='选择要读取的文件…', filter='*.xlsx')
    return filename
