# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from ..services import MessageService

import subprocess
import os
from wulifang._util import env_set

class _MessageServiceImpl:
    def debug(self, message, title=""):
        # type: (Text, Text) -> None
        pass

    def info(self, message, title=""):
        # type: (Text, Text) -> None
        pass

    def error(self, message, title=""):
        # type: (Text, Text) -> None
        env = os.environ.copy()
        env_set(env, "INPUT_MESSAGE" , message)
        env_set(env, "INPUT_TITLE" , title or "Error")
        subprocess.Popen(
            ["PowerShell", "-Version", "2",  "-NoProfile" ,"-Sta", "-Command", """\
Add-Type -AssemblyName PresentationFramework
[void][System.Windows.MessageBox]::Show($env:INPUT_MESSAGE, $env:INPUT_TITLE, [System.Windows.MessageBoxButton]::OK, [System.Windows.MessageBoxImage]::Error)
        """],
            env=env,
        )


def new_wpf_message_service():
    # type: () -> MessageService
    return _MessageServiceImpl()


if __name__ == '__main__':
    s = new_wpf_message_service()
    s.debug("debug", title="title1")
    s.info("info", title="title2")
    s.error("error", title="title3")
    s.error("错误", title="标题3")
