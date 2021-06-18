# -*- coding=UTF-8 -*-
# pyright: strict
"""import asset link workbook.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
from typing import Text

import cast_unknown as cast
import cgtwq
import filetools
import openpyxl 
import win_unicode_console
import xlsxtools

__version__ = "2021.06.18"
LOGGER = logging.getLogger(__name__)

HEADER_ALIAS = {
    'asset': ('资产',),
    'shot': ('镜头',),
}

def _link(db, asset, shot):
    # type: (cgtwq.Database, Text, Text) -> ...
    asset_module = db.module("asset", "info")
    shot_module = db.module("shot", "info")
    assets = asset_module.filter(cgtwq.Field("asset.asset_name") == asset, namespace="asset")
    if not assets:
        LOGGER.warning("not found asset: %s", asset)

    shots = shot_module.filter(cgtwq.Field("shot.shot") == shot, namespace="shot")
    if not shot:
        LOGGER.warning("not found asset: %s", asset)
    shots.link.link(*assets) # type: ignore
    LOGGER.info("link: asset=%s, shot=%s", asset, shot)


def main():
    client = cgtwq.DesktopClient()
    client.connect()
    win_unicode_console.enable()
    logging.basicConfig(
        level='INFO', 
        format='%(levelname)-7s:%(name)s: %(message)s',
    )

    print('{:-^50}'.format('Link 导入 v{}'.format(__version__)))
    print("""\
所需表格格式：

| 镜头                  | 资产   |
| --------------------- | ------ |
| SDKTEST_EP01_01_sc001 | asset1 |
| SDKTEST_EP01_01_sc002 | asset1 |

镜头支持别名：shot
资产支持别名：asset

镜头的值为 shot.shot 字段
资产的值为 asset.asset_name 字段
""")
    client = cgtwq.DesktopClient()
    client.connect()
    plugin_data = client.plugin.data() # type: ignore
    db = cgtwq.Database(cast.text(plugin_data.database)) # type: ignore

    filename = filetools.ask_filename()
    if not filename:
        return
    workbook = openpyxl.load_workbook(filename)

    for i in xlsxtools.iter_workbook_as_dict(workbook, HEADER_ALIAS):
        asset = i.get("asset")
        shot = i.get("shot")
        if asset and shot:
            _link(db, cast.text(asset), cast.text(shot))
        else:
            LOGGER.warning("忽略不支持的数据: %s", cast.binary(i).decode("unicode-escape"))

if __name__ == '__main__':
    main()

