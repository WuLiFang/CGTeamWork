# -*- coding=UTF-8 -*-
"""Assign downstream task to current artists.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging

import win_unicode_console

import cgtwq
from wlf.console import pause

DOWNSTREAM_DICT = {'灯光': ['渲染', '预渲染'],
                   '合成': ['输出']}
LOGGER = logging.getLogger(__name__)


def assign_same_to_downstream(select):
    """Assign downstream task to current artists.  """

    assert isinstance(select, cgtwq.Selection)
    pipeline = select.pipeline.one()
    current_data = select.get_fields('shot.shot', 'account_id')

    target = select.module.filter(
        cgtwq.Field('shot.shot').in_(current_data.column('shot.shot')),
        cgtwq.Field('pipeline').in_(DOWNSTREAM_DICT[pipeline.name]))
    target_data = target.get_fields(
        'id',
        'shot.shot',
        'account_id',
        'pipeline',
    )

    for shot, account_id in current_data:
        account_ids = set(account_id.split(','))
        for _id, _, target_account_id, pipeline in (
                i for i in target_data
                if i[1] == shot
        ):
            target_account_ids = set(target_account_id.split(','))
            if target_account_ids == account_ids:
                LOGGER.info('跳过已设置: %s: %s', pipeline, shot)
                continue
            LOGGER.info(
                '设置制作者: %s: %s: %s -> %s',
                pipeline,
                shot,
                target_account_ids,
                account_ids,
            )
            select.module.select(_id).flow.assign(account_ids)


def main():
    logging.basicConfig(level=logging.INFO)

    win_unicode_console.enable()
    client = cgtwq.DesktopClient()
    client.connect()
    select = client.selection()

    try:
        assign_same_to_downstream(select)
        pause(5)
    except KeyError:
        LOGGER.error('当前仅支持流程: {}'.format(','.join(DOWNSTREAM_DICT.keys())))
        pause(0)
    except:
        import traceback
        traceback.print_exc()
        pause(0)
        raise


if __name__ == '__main__':
    main()
