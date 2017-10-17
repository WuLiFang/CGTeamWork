# -*- coding=UTF-8 -*-
"""Cgteamwork uploader entry. """

from wlf import uploader
from wlf.mp_logging import set_basic_logger
import logging

set_basic_logger()
logging.getLogger().setLevel(logging.DEBUG)

uploader.main()
