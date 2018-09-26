# -*- coding=UTF-8 -*-
"""Transfer task status from downstream to upstream.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import cgtwq

LOGGER = logging.getLogger(__name__)


def transfer(plugin_data, status='Approve',
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

    LOGGER.info('传递状态: %s: %s -> %s', status, from_, target)
    assert isinstance(plugin_data, cgtwq.model.PluginData), type(plugin_data)
    database = cgtwq.Database(plugin_data.database)
    module = database[plugin_data.module]
    assert isinstance(module, cgtwq.Module)
    select = module.select(*plugin_data.id_list)
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
        module.select(*transfer_id_list).set_fields(**
                                                    {i: status for i in target})

        LOGGER.info('为%s个条目传递了状态', len(transfer_id_list))
    else:
        LOGGER.info('检查了%s个条目, 不需传递状态', len(plugin_data.id_list))


def main():
    logging.basicConfig(level=logging.INFO)
    # LOGGER.setLevel(logging.DEBUG)
    client = cgtwq.DesktopClient()
    client.connect()
    transfer(client.plugin.data())
