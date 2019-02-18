# -*- coding=UTF-8 -*-
"""Update retake count field for current selection.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
from collections import namedtuple

import win_unicode_console

import cgtwq

__version__ = '0.1.0'

FieldData = namedtuple(
    'FieldData', ('status_field_sign', 'retake_count_field_sign', 'label', 'step'))

RETAKE_COUNT_FIELDS = [
    FieldData('task.leader_status',
              'task.leader_retake_count',
              "组长返修次数",
              '组长状态'),
    FieldData('task.director_status',
              'task.director_retake_count',
              "导演返修次数",
              '导演状态'),
    FieldData('task.client_status',
              'task.client_retake_count',
              "客户返修次数",
              '客户状态'),
]
# type: List[FieldData]

LOGGER = logging.getLogger(__name__)


def setup_fields(module):
    """Create retake count field if needed.  """
    # type: (cgtwq.Module,) -> None

    exists_field_signs = [i.sign for i in module.field.meta()]
    for i in RETAKE_COUNT_FIELDS:
        if i.retake_count_field_sign in exists_field_signs:
            continue
        module.field.create(i.retake_count_field_sign, "int", label=i.label)
        LOGGER.info('Created field: %s', i.retake_count_field_sign)


def update_entry(entry):
    """Update entry retake count.  """
    # type: (cgtwq.Entry,) -> None

    result = {}
    for i in RETAKE_COUNT_FIELDS:
        value = (entry
                 .history
                 .count((cgtwq.Field('step') == i.step)
                        & (cgtwq.Field('status') == 'Retake')))
        result[i.retake_count_field_sign] = value
    entry.set_fields(**result)
    LOGGER.info('Updated entry: %s: %s', entry, result)


def main():
    win_unicode_console.enable()
    logging.basicConfig(
        level='INFO', format='%(levelname)-7s:%(name)s: %(message)s')

    print('更新返修次数 v{}'.format(__version__))
    client = cgtwq.DesktopClient()
    client.connect()
    select = client.selection()
    setup_fields(select.module)
    for i in select.to_entries():
        update_entry(i)


if __name__ == '__main__':
    main()
