# -*- coding=UTF-8 -*-
"""Get and link assets from maya file.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import logging
import os
import re
import sys
from os.path import basename, join, splitext
from subprocess import PIPE, Popen

import wlf
from wlf.cgtwq import CGTeamWorkClient, Database, Filter
from wlf.notify import progress
from wlf.path import get_encoded as e

ASSET_NAME_FILTERS = []


def get_references(filename, database=None):
    """Get references file list from a maya file.

    Args:
        filename (str): Filename.

    Returns:
        list: References list.
    """

    database = database or Database(
        CGTeamWorkClient.get_plugin_data().database)
    mayabatch = database.get_software('mayabatch')
    cmd = ('{} -file {} '
           '-command "python(\\"import json;import pymel.all;'
           '\'\\\\n\\\\n\' '
           '+ json.dumps([i.path for i in pymel.all.listReferences()]) '
           '+ \'\\\\n\\\\n\'\\")"').format(mayabatch, filename)

    logging.info('Reading maya file: %s', filename)
    proc = Popen(e(cmd), stdout=PIPE)
    stdout, _ = proc.communicate()

    result = re.findall('\n\n(\\[.*\\])\n\n'.replace('\n', os.linesep), stdout)
    if len(result) > 1:
        logging.warning('Multiple result: %s', result)

    return json.loads(result[0])


def get_assets(filename_list, database=None):
    """Get asset id from filename.

    Args:
        filename_list (list): Fliename lise.
        database (Database, optional): Defaults to None. 
            Search asset in this database.

    Returns:
        tuple: Asset id.
    """

    database = database or Database(
        CGTeamWorkClient.get_plugin_data().database)

    def _get_name(filename):
        ret = splitext(basename(filename))[0]
        ret = re.sub('(?i)_Hi|_Lo$', '', ret)
        for i in ASSET_NAME_FILTERS:
            ret = i(ret)
        return ret

    names = [_get_name(i) for i in filename_list]
    select = database['asset'].filter(Filter('asset_name', names))
    data = select.get_fields('id', 'asset_name')
    assets_names = data.field('asset_name')

    for i in names:
        if i not in assets_names:
            logging.warning('Not found matched asset: %s', i)
        else:
            logging.info('Found asset: %s', i)

    return data.field('id')


def link_assets(task_id, database=None):
    """Link asset for a task.

    Args:
        task_id (unicode): Task uuid.
        database (Database, optional): Defaults to None. 
            Database the `task_id` belongs.
    """

    database = database or Database(
        CGTeamWorkClient.get_plugin_data().database)
    assert isinstance(database, Database)

    select = database['shot_task'].select(task_id)
    pipeline = select['pipeline'][0]
    pipeline_id = database.get_pipline(Filter('name', pipeline))[0].id
    filebox = database.get_filebox(Filter('title', 'Maya最终文件')
                                   & Filter('#pipeline_id', pipeline_id))[0]

    filebox_info = select.get_filebox(id_=filebox.id)
    dir_ = filebox_info.path
    for filename in os.listdir(dir_):
        filepath = join(dir_, filename)
        assets = get_assets(get_references(filepath, database), database)
        select.link(*assets)


def link_current_selected():
    """Link asset for current selected items.
    """

    plugin = CGTeamWorkClient.get_plugin_data()

    # Set up special rules.
    if plugin.database == 'proj_mt':
        ASSET_NAME_FILTERS.append(lambda x: x.replace('MT_S1_', ''))

    database = Database(plugin.database)
    select = database[plugin.module].select(*plugin.id_list)
    data = select.get_fields('id', 'shot.shot')
    dict_ = {i[1]: i[0] for i in data}
    for i in progress(data.field('shot.shot'), 'link资产'):
        link_assets(dict_[i], database)
    CGTeamWorkClient.refresh_select(plugin.database, plugin.module)


def main():
    wlf.mp_logging.basic_config(level=logging.INFO)
    link_current_selected()


if __name__ == '__main__':
    main()
