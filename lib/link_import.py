# -*- coding=UTF-8 -*-
# pyright: strict
"""import asset link workbook.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
from typing import Text, Tuple

import cast_unknown as cast
import cgtwq
import six
import filetools
import openpyxl
import win_unicode_console
import xlsxtools

__version__ = "2021.06.23"
LOGGER = logging.getLogger(__name__)

HEADER_ALIAS = {
    "shot": ("镜头",),
}


def _link(db, shot, assets):
    # type: (cgtwq.Database, Text, Tuple[Text, ...]) -> ...
    if not assets:
        return
    asset_module = db.module("asset", "info")
    shot_module = db.module("shot", "info")
    try:
        matched_assets = asset_module.filter(
            cgtwq.Field("asset.asset_name").in_(assets), namespace="asset"
        )
        if len(matched_assets) != len(assets):
            LOGGER.warning(
                "some asssets not found: assets=%s match=%d", assets, len(matched_assets)
            )
    except cgtwq.EmptySelection:
        LOGGER.warning("not found assets: %s", assets)
        return
    try:
        shots = shot_module.filter(cgtwq.Field("shot.shot") == shot, namespace="shot")
    except cgtwq.EmptySelection:
        LOGGER.warning("not found shot: %s", shot)
        return
    shots.link.link(*matched_assets)  # type: ignore
    LOGGER.info("link: shot=%s, assets=%s", shot, assets)


def main():
    client = cgtwq.DesktopClient()
    client.connect()
    win_unicode_console.enable()
    logging.basicConfig(
        level="INFO",
        format="%(levelname)-7s:%(name)s: %(message)s",
    )

    print("{:-^50}".format("Link 导入 v{}".format(__version__)))
    print(
        """\
所需表格格式：

| 镜头                  | 资产1   | 资产2   |
| --------------------- | ------ | ------- |
| SDKTEST_EP01_01_sc001 | asset1 | asset2 |
| SDKTEST_EP01_01_sc002 | asset1 |


必须有命名为镜头(支持别名：shot)的列，所有其他表头不为空的列将视为资产。

镜头的值为 shot.shot 字段
资产的值为 asset.asset_name 字段
"""
    )
    client = cgtwq.DesktopClient()
    client.connect()
    plugin_data = client.plugin.data()  # type: ignore
    db = cgtwq.Database(cast.text(plugin_data.database))  # type: ignore

    filename = filetools.ask_filename()
    if not filename:
        return
    workbook = openpyxl.load_workbook(filename)

    for i in xlsxtools.iter_workbook_as_dict(workbook, HEADER_ALIAS):
        shot = i.get("shot")
        if shot:
            _link(
                db,
                cast.text(shot),
                tuple(
                    cast.text(v)
                    for k, v in six.iteritems(i)
                    if (k and v and k != "shot")
                ),
            )
        else:
            LOGGER.warning("忽略不支持的数据: %s", cast.binary(i).decode("unicode-escape"))


if __name__ == "__main__":
    main()
