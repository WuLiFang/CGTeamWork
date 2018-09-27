# -*- coding=UTF-8 -*-
"""AIA manage plugin."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import stat
from itertools import chain

import win_unicode_console

import cgtwq
from wlf.codectools import get_encoded as e
from wlf.console import pause

__version__ = '0.3.0'


LOGGER = logging.getLogger(__name__)


def get_filebox_meta(select):
    """Get filebox for final files.  """

    assert isinstance(select, cgtwq.Selection), type(select)
    pipelines = select.pipeline.all()
    assert pipelines
    fileboxes = select.module.database.filebox.filter(
        cgtwq.Field('title').has('最终'),
        cgtwq.Field('#pipeline_id').in_([i.id for i in pipelines])
    )
    if not fileboxes:
        raise RuntimeError('No matched fileboxes')
    elif len(fileboxes) != 1:
        raise RuntimeError('Multiple matched filebox', fileboxes)
    ret = fileboxes[0]
    assert isinstance(ret, cgtwq.model.FileBoxMeta)
    return ret


def set_readonly(select):
    """Set final files readonly. """

    for i in get_files(select):
        os.chmod(e(i), stat.S_IREAD)
        LOGGER.info('设为只读: %s', i)


def set_writable(select):
    """Set final files writable. """

    for i in get_files(select):
        os.chmod(e(i), stat.S_IWRITE)
        LOGGER.info('设为读写: %s', i)


def get_files(select):
    """Get final files from selection.

    Args:
        select (cgtwq.Selection): Selection.

    Returns:
        Generator[str]: Files
    """

    assert isinstance(select, cgtwq.Selection), type(select)
    filebox_meta = get_filebox_meta(select)
    files = chain()
    for i in select.to_entries():
        assert isinstance(i, cgtwq.Entry)
        filebox = i.filebox.get(id_=filebox_meta.id)
        files = chain(files, walk(filebox.path))
    return files


def walk(path):
    """(Generator)Walk through path. Ignore `history` forlder.

    Args:
        path (str): Path.
    """

    path = e(path)
    for dirpath, dirnames, filenames in os.walk(path):
        try:
            dirnames.remove('history')
        except ValueError:
            pass
        for i in filenames:
            yield os.path.join(dirpath, i)


def transfer(select,
             status='Approve',
             from_=('define_jba', 'client_status'),
             target=('status',)):
    """Transfer status from multiple field to multiple filed.

    Args:
        plugin_data (cgtwq.client.PluginData): Data for plugin.
        status (str, optional): Defaults to 'Approve'. Status value to transfer.
        from_ (tuple, optional): Defaults to ('define_jba', 'client_status').
            Tuple for Server defined status field.
        target (tuple, optional): Defaults to ('status',).
            Tuple for Server defined status field.
    """

    assert isinstance(select, cgtwq.Selection), type(select)
    LOGGER.info('传递状态: %s: %s -> %s', status, from_, target)
    data = select.get_fields('id', *(from_+target))

    transfer_id_list = []
    for i in list(data):
        assert isinstance(i, list)
        id_ = i.pop(0)
        from_data = i[:len(from_)]
        to_data = i[-len(target):]
        LOGGER.debug('%s: %s -> %s', id_, from_data, to_data)
        if (all(i == status for i in from_data)
                and any(i != status for i in to_data)):
            transfer_id_list.append(id_)

    if transfer_id_list:
        select.module.select(*transfer_id_list).set_fields(**
                                                           {i: status for i in target})

        LOGGER.info('为%s个条目传递了状态', len(transfer_id_list))
    else:
        LOGGER.info('检查了%s个条目, 不需传递状态', len(select))


def block(select, field):
    """Block drag in when task already approved.  """

    assert isinstance(select, cgtwq.Selection), type(select)
    client = cgtwq.DesktopClient()
    if any(i == 'Approve' for i in select[field]):
        client.plugin.send_result(False)


win_unicode_console.enable()


def main():
    """Get plugin setting from cgtw.  """
    logging.basicConfig(level=logging.INFO)

    print('AIA_manage v{}'.format(__version__))
    client = cgtwq.DesktopClient()
    client.connect()
    metadata = client.plugin.metadata()
    select = client.selection()

    func = {
        'set_readonly': set_readonly,
        'set_writable': set_writable,
        'transfer': transfer,
        'block': lambda select: block(select, metadata.arguments['field'])
    }[metadata.arguments['operation']]

    try:
        func(select)
    except:
        client.plugin.send_result(False)
        raise


if __name__ == '__main__':
    win_unicode_console.enable()
    try:
        main()
    except:
        import traceback
        traceback.print_exc()
        pause()
        raise
