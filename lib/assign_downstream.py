# -*- coding=UTF-8 -*-
"""Assign downstream task to current artists.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pprint

import win_unicode_console

import cgtwq
from wlf.console import pause

DOWNSTREAM_DICT = {'灯光': '渲染',
                   '合成': '输出'}


def assign_same_to_downstream(select):
    """Assign downstream task to current artists.  """

    assert isinstance(select, cgtwq.Selection)
    pipeline = select.pipeline.one()
    current_data = select.get_fields('shot.shot', 'account_id')

    target = select.module.filter(
        cgtwq.Field('shot.shot').in_(current_data.column('shot.shot')),
        cgtwq.Field('pipeline') == DOWNSTREAM_DICT[pipeline.name])
    target_data = target.get_fields('id', 'shot.shot', 'account_id')

    errored_shots = []

    for shot, account_id in current_data:
        try:
            _target = select.module.select(
                *[i[0] for i in target_data
                  if i[1] == shot])
            assert len(_target) == 1, _target
            _target_data = (i for i in target_data if i[0] in _target)
        except ValueError:
            errored_shots.append(shot)
            continue

        account_ids = set(account_id.split(','))
        target_account_ids = set(j
                                 for i in _target_data
                                 for j in i[2].split(','))

        if target_account_ids == account_ids:
            print('跳过已设置: {}'.format(shot))
            continue
        print('设置制作者: {}: {} -> {}'.format(shot, target_account_ids, account_ids))
        _target.flow.assign(account_ids)

    if errored_shots:
        print('以下镜头无输出阶段:')
        pprint.pprint(errored_shots)
    return errored_shots


def main():
    win_unicode_console.enable()
    client = cgtwq.DesktopClient()
    client.connect()
    select = client.selection()

    try:
        errored_shots = assign_same_to_downstream(select)
        pause(0 if errored_shots else 5)
    except KeyError:
        print('当前仅支持流程: {}'.format(','.join(DOWNSTREAM_DICT.keys())))
        pause(0)
    except:
        import traceback
        traceback.print_exc()
        pause(0)
        raise


if __name__ == '__main__':
    main()
