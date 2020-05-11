# coding=utf-8
"""Export task history.  """

from __future__ import print_function, unicode_literals

import logging
import os
import sys
import typing  # pylint:disable=unused-import
import webbrowser
from datetime import datetime

import openpyxl
from bs4 import BeautifulSoup
from Qt.QtWidgets import QApplication, QFileDialog, QMessageBox

import cgtwq
import wlf.mp_logging

LOGGER = logging.getLogger()

__version__ = '0.4.0'


def parse_html_comment(value):
    """Parse history text.  """

    soup = BeautifulSoup(value, 'html.parser')
    images = soup.findAll('img')
    links = []
    ret = {
        'images': [],
    }

    for i in images:
        src = i.get('src')
        if not src:
            continue
        ret['images'].append(src)
    value = soup.get_text(strip=True).replace(
        'p, li { white-space: pre-wrap; }', '')
    ret['text'] = value

    return ret


L10N_MESSAGES = {
    'status.Approve': '通过',
    'status.Retake': '返修',
}


def tr(key):
    return L10N_MESSAGES.get(key, key)


def msgbox(message, detail=None):
    msgbox = QMessageBox()
    msgbox.setText(message)
    if detail:
        msgbox.setDetailedText(detail)
    return msgbox.exec_()


def get_rows(select):
    # type: (cgtwq.Selection) -> List[Dict]

    histories = select.history.get(cgtwq.Field(
        'status').in_(['Retake', 'Approve']))

    tasks = set([i.task_id for i in histories])
    tasks = select.module.select(*tasks)
    tasks = tasks.get_fields("id", "shot.shot", "pipeline", "artist")
    tasks = {i[0]: dict(shot=i[1], pipeline=i[2], artist=i[3]) for i in tasks}
    ret = []
    history_by_task = {}
    for i in histories:
        history_by_task.setdefault(i.task_id, []).append(i)
    history_by_task = {
        k: sorted(v, reverse=True, key=lambda x: x.time)
        for k, v
        in history_by_task.iteritems()}
    for i in histories:  # type: cgtwq.model.HistoryInfo
        task = tasks[i.task_id]
        row = dict(task)
        row.update(
            html=i.text,
            created_by=i.create_by,
            time=i.time,
            status=tr("status."+i.status),
            step=i.step,
            order=history_by_task[i.task_id].index(i) + 1
        )
        ret.append(row)

    return sorted(ret, key=lambda x: (x['shot'], x['pipeline'], x['order']))


def create_workbook(rows):
    # type: (typing.List[typing.Dict]) -> openpyxl.Workbook

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(
        ['镜头', '流程', '制作者', '状态',
         '时间', '顺序(最新为1)', "阶段", '操作用户', '备注'])
    sheet.freeze_panes = 'A2'
    server_ip = cgtwq.DesktopClient().server_ip
    for i in rows:
        row = [
            i['shot'],
            i['pipeline'],
            i['artist'],
            i['status'],
            i['time'],
            i['order'],
            i['step'],
            i['created_by'],
        ]
        note = parse_html_comment(i['html'])
        if note['text']:
            row.append(note['text'])
        for img in note['images']:
            link = u'=HYPERLINK("http://{}/{}","[{}]")'.format(
                server_ip,
                img,
                os.path.basename(img))
            row.append(link)
        sheet.append(row)
    return book


def main():
    print('{:-^50s}'.format('导出历史 v{}'.format(__version__)))
    wlf.mp_logging.basic_config()
    dummy_app = QApplication(sys.argv)
    filename, _ = QFileDialog.getSaveFileName(
        None, '保存位置', 'E:/任务历史-{}.xlsx'.format(datetime.now().strftime('%Y%m%d-%H%M')), '*.xlsx')
    if not filename:
        return
    client = cgtwq.DesktopClient()
    client.connect()
    pipeline = set(client.selection().get_fields(
        "pipeline").column("pipeline"))
    select = client.selection().module.filter(
        cgtwq.Field("pipeline").in_(list(pipeline)),
    )
    try:
        rows = get_rows(select)
        wb = create_workbook(rows)
        wb.save(filename)
        webbrowser.open(os.path.dirname(filename))
    except IOError:
        LOGGER.error('不能写入文件: %s', filename)
        msgbox('不能写入文件: {}, 请检查文件占用'.format(filename))


if __name__ == '__main__':
    main()
