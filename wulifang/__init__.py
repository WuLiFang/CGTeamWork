# -*- coding=UTF-8 -*-
# pyright: strict,reportTypeCommentUsage=false
"""WuLiFang cgteamwork plugin.  """

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from .services import (
        MessageService,
    )

import os



def _default_message():
    # type: () -> MessageService
    from .infrastructure.logging_message_service import (
       LoggingMessageService,
    )
    from .infrastructure.multi_message_service import (
       MultiMessageService,
    )
    from .infrastructure.wpf_message_service import new_wpf_message_service
    return MultiMessageService(
        LoggingMessageService(),
        new_wpf_message_service(),
    )


# services
# should been set during init
message = _default_message() 
is_debug = os.getenv("DEBUG") == "wulifang"

