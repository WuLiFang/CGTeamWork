# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

from ._compat import PY2

import sys

_ENCODING =  "mbcs" if sys.platform =="win32" else "utf-8"

def env_set(env, k, v):
    # type: (dict[Text,Text], Text, Text) -> None
    if PY2:
        env[k.encode(_ENCODING)] = v.encode(_ENCODING) # type: ignore
        return
    env[k] = v
    return 
