# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional, Text


from cgtwq.desktop import new_client
from cgtwq import RowID, F
from string import Template
from six import iteritems
import logging

_LOGGER = logging.getLogger(__name__)


class RowData:
    def __init__(self, status, pipeline):
        # type: (Text, Text) -> None
        self.status = status
        self.pipeline = pipeline


def main():
    client = new_client()
    ctx = client.plugin.context()
    _LOGGER.debug("plugin context: %s", ctx.raw)
    argv = ctx.argv
    if len(argv) < 5:
        plugin = client.plugin.get(ctx.plugin_id)
        argv = plugin.argv()
        argv.add("selectStatus", "必填，插件只对指定状态的任务进行处理。多个状态用英文逗号分隔。")
        argv.add("fieldSign", "选填，要变更的状态字段，默认为触发的字段。")
        argv.add("activeStatus", "选填，设置活跃（没有上游任务）任务为此状态。")
        argv.add("pendingStatus", "选填，设置待办（有上游任务）任务为此状态。")
        argv.add(
            "message",
            "选填，设置更改状态时的消息。支持变量： ${activePipeline}=活跃流程名称 ${activeStatus}=活跃状态名称 ${pendingStatus}=待办状态名称",
        )
        raw_argv = argv.encode()
        if raw_argv != plugin.raw_argv:
            plugin.raw_argv = raw_argv
            client.plugin.save(plugin, only_fields=["argv"])
            _LOGGER.info("update plugin arguments")
    field_sign = argv["fieldSign"] or ctx.qc_field_sign.value
    select_status = argv["selectStatus"].split(",")
    active_status = argv["activeStatus"]
    pending_status = argv["pendingStatus"]
    messageTemplate = Template(argv["message"])
    if not select_status:
        raise ValueError("`selectStatus` 参数为必填")

    module_ids = tuple(set(client.table(
        ctx.database,
        ctx.module,
        ctx.module_type,
        filter_by=F("%s.id" % (ctx.module_type, )).in_(ctx.id_list),
    ).column("%s.id" % ctx.module)))
    selected_rows = {
        RowID(ctx.database, ctx.module, ctx.module_type, id): RowData(status, pipeline)
        for id, status, pipeline in client.table(
            ctx.database,
            ctx.module,
            ctx.module_type,
            filter_by=F(field_sign)
            .in_(select_status)
            .and_(F("%s.id" % (ctx.module,)).in_(module_ids)),
        ).rows("%s.id" % (ctx.module_type,), field_sign, "pipeline.entity")
    }

    edges = set()  # type: set[tuple[RowID, RowID]]
    nodes = set()  # type: set[RowID]
    def _on_row_id(id):
        # type: (RowID) -> None
        if id in nodes:
            return
        nodes.add(id)
        res = client.pipeline.neighbor_task(id)
        for i in res.next():
            edges.add((id, i))

        for i in res.previous():
            edges.add((i, id))
            _on_row_id(i)
    for id in selected_rows:
        _on_row_id(id)

    def _find_active(i):
        # type: (RowID) -> Optional[RowID]
        for up, down in edges:
            if down != i:
                continue
            v = _find_active(up)
            if v:
                return v
        if i in selected_rows:
            return i
        return None

    def _render_msg(active):
        # type: (RowID) -> Text
        table = client.table(
            active.database,
            active.module,
            active.module_type,
            filter_by=F("%s.id" % active.module_type).equal(active.value),
        )
        data = dict(
            activeStatus=active_status,
            pendingStatus=pending_status,
        )
        if "activePipeline" in messageTemplate.template:
            data["activePipeline"] =  ",".join(table.column("pipeline.entity"))

        return messageTemplate.substitute(data)

    for id, data in iteritems(selected_rows):
        active_id = _find_active(id)
        assert active_id, "every select id should has a active id"
        is_active = id == active_id
        target_status = active_status if is_active else pending_status
        if target_status and data.status != target_status:
            msg = _render_msg(active_id)
            _LOGGER.info(
                "[%s->%s]%s(%s): %s", data.status, target_status, data.pipeline, id, msg
            )
            client.flow.update(id, field_sign, target_status, msg)
            client.view.refresh_row(id)
        else:
            _LOGGER.info("[%s]%s(%s)", data.status, data.pipeline, id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
