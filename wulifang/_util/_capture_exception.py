# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from wulifang.services import MessageService
    from typing import Optional, Generator

import contextlib
import traceback


def _default_message():
    import wulifang

    if wulifang.message is None: # type: ignore
        from wulifang.infrastructure.logging_message_service import (
            LoggingMessageService,
        )

        return LoggingMessageService()
    return wulifang.message


@contextlib.contextmanager
def capture_exception(format="%s", message=None):
    # type: (str, Optional[MessageService]) -> Generator[None, None, None]
    message = message or _default_message()
    try:
        yield
    except Exception as ex:
        traceback.print_exc()
        message.error(format % (ex,))
