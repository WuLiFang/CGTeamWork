# -*- coding=UTF-8 -*-
"""Entry for Cgteamwork. """

import os
import subprocess
import sys
from os.path import dirname

import wlf

subprocess.Popen([sys.executable.replace('python.exe','pythonw.exe'), '-m', 'wlf.csheet'], env=os.environ.update({'PYTHONPATH':dirname(__file__)}))
