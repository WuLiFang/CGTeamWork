# -*- coding=UTF-8
"""Local site for share on server.  """
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import site
import subprocess
import sys

__dirname__ = os.path.dirname(os.path.abspath(__file__))
LOCAL_SITE_DIR = os.path.join(__dirname__, ".venv", "lib", "site-packages")


def main():
    """Run incoming arguments with python in configured environment."""

    sys.path.insert(0, __dirname__)
    site.addsitedir(LOCAL_SITE_DIR)
    os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
    sys.exit(subprocess.call([sys.executable] + sys.argv[1:], cwd=__dirname__))


if __name__ == "__main__":
    main()
