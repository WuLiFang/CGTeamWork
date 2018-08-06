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
    data = select.get_fields('shot.shot', 'account_id', 'pipeline')
    pipeline = data.column('pipeline')
    assert len(pipeline) == 1, '选择了多个流程: {}'.format(pipeline)
    pipeline = pipeline[0]
    target_select = select.module.filter((cgtwq.Field('shot.shot').in_(data.column('shot.shot')))
                                         & (cgtwq.Field('pipeline') == DOWNSTREAM_DICT[pipeline]))
    target_data = target_select.get_fields('id', 'shot.shot', 'account_id', )
    errored_shots = []
    for shot, account_id, _ in data:
        account_ids = set(account_id.split(','))
        try:
            target = select.module.select(
                *[i[0] for i in target_data if i[1] == shot])
        except ValueError:
            errored_shots.append(shot)
            continue
        assert len(target) == 1, target

        target_account_ids = set(i
                                 for j in target_data if j[0] in target
                                 for i in j[2].split(','))
        if target_account_ids == account_ids:
            print('跳过已设置: {}'.format(shot))
            continue
        print('设置制作者: {}: {} -> {}'.format(shot, target_account_ids, account_ids))
        target.flow.assign(account_ids)

    if errored_shots:
        print('以下镜头无输出阶段:')
        pprint.pprint(errored_shots)
    return errored_shots


def main():
    win_unicode_console.enable()
    cgtwq.update_setting()
    plugin_data = cgtwq.DesktopClient.get_plugin_data()
    select = cgtwq.Database(
        plugin_data.database
    ).module(
        plugin_data.module, module_type=plugin_data.module_type
    ).select(*plugin_data.id_list)

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
