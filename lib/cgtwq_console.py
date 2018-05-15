# -*- coding=UTF-8 -*-
"""Cgtwq console for manual operation. """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import cgtwq


def main():
    cgtwq.update_setting()
    plugin_data = cgtwq.client.DesktopClient.get_plugin_data()
    database = cgtwq.Database(plugin_data.database)
    module = database[plugin_data.module]
    select = module.select(*plugin_data.id_list)
    __main__ = sys.modules['__main__']

    for k, v in {'DATABASE': database,
                 'MODULE': module,
                 'SELECT': select}.items():
        setattr(__main__, k, v)

    print('''
已设置变量:
    DATABASE: 当前数据库对象
    MODULE: 当前模块对象
    SELECT: 当前所选对象''')


if __name__ == '__main__':
    main()
