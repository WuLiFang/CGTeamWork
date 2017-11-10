# coding=utf-8
"""Export task history.  """

from __future__ import print_function, unicode_literals

import logging
import os
import sys
import webbrowser
import unittest

from bs4 import BeautifulSoup

from wlf.mp_logging import set_basic_logger
from wlf.table import RowTable
from wlf.Qt.QtWidgets import QApplication, QFileDialog
from wlf.notify import Progress, CancelledError, message_box

from cgtwb import Current

LOGGER = logging.getLogger()
if __name__ == '__main__':
    set_basic_logger()

__version__ = '0.3.1'


class CurrentHistory(RowTable):
    """Retake/Approve history of current module.  """

    l10n_dict = {
        '^note$': '备注',
        '^text$': '文本',
        '^name$': '名称',
        r'^image(\d*)': r'图片\1',
        '^time$': '时间',
        '^step$': '流程',
        '^pipeline$': '制作阶段',
        '^Approve$': '通过',
        '^Retake$': '返修',
        '^status$': '状态',
        '^artist$': '制作者',
    }

    def __init__(self):
        super(CurrentHistory, self).__init__()
        current = Current()
        task_module = current.task_module
        signs = current.signs

        filters = []
        for i in current.selected_ids:
            filters.append(['#task_id', '=', i])
            filters.append('or')
        filters.pop(-1)

        infos = current.history_module.get_with_filter(
            ['time', 'text', 'status', '#account_id', '#task_id', 'step'],
            filters)

        if not isinstance(infos, list):
            raise ValueError(infos)

        infos = [i for i in infos if i['status'] in ('Retake', 'Approve')]
        if not infos:
            message_box('所选条目没有返修历史')
            raise ValueError

        task_module.init_with_id([i['task_id'] for i in infos])

        self.task_infos = task_module.get(
            [signs['name'], signs['artist'], signs['pipeline']])

        task = Progress('获取信息', total=len(infos))
        task_infos = {}
        for info in infos:
            if not info:
                continue
            name = self.get_task_info(info['task_id'], signs['name'])
            pipeline = self.get_task_info(info['task_id'], signs['pipeline'])
            task_infos.setdefault((name, pipeline), {})
            task_info = task_infos[(name, pipeline)]
            step = info['step']
            task_info.setdefault(step, {})
            records = task_info[step]
            record_name = 'record_{:02d}'.format(len(records) + 1)
            records.setdefault(record_name, {})
            record = records[record_name]

            task_info['name'] = name
            task_info['pipeline'] = pipeline
            task_info['artist'] = self.get_task_info(
                info['task_id'], signs['artist'])

            record.update(self.parse_html_to_xls(info['text']))
            record['time'] = info['time']
            record['status'] = info['status']

            task.step(name)

        for key in sorted(task_infos.keys()):
            self.append(task_infos[key])

        def _get_row(header, index):
            ret = header
            try:
                for _ in range(index):
                    ret = ret[1]
                ret = ret[0]
            except IndexError:
                ret = None
            return ret

        self.header.sort(key=lambda x: (x[0] != 'name',
                                        x[0] != 'pipeline',
                                        x[0] != 'artist',
                                        x[0] != '组长状态',
                                        x[0] != '导演状态',
                                        x[0] != '客户状态',
                                        x[0] != 'AIA',
                                        _get_row(x, 1),
                                        _get_row(x, 2) != 'status',
                                        _get_row(x, 2) != 'text',
                                        _get_row(x, 2) == 'time',
                                        x))

    def get_task_info(self, task_id, name, default=None):
        """Get task info by @task_id and info @name.  """

        ret = [i for i in self.task_infos if i['id'] == task_id]
        if ret:
            ret = ret[0][name]
        else:
            ret = default
        return ret

    def parse_html_to_xls(self, value):
        """Parse history text.  """

        soup = BeautifulSoup(value, 'html.parser')
        images = soup.findAll('img')
        links = []
        ret = {}
        if images:
            for i in images:
                link = u'http://{}/{}'.format(Current().server_ip,
                                              i.get('src'))
                links.append(link)
        value = soup.get_text(strip=True).replace(
            'p, li { white-space: pre-wrap; }', '')

        if links:
            for index, link in enumerate(links, 1):
                xls_func = u'=HYPERLINK("{}","[{}]")'.format(
                    link, os.path.basename(link))

                ret['image_{}'.format(index)] = xls_func
            value = value or '[仅有图片]'
        ret['text'] = value

        return ret


def main():
    print('{:-^50s}'.format('导出历史 v{}'.format(__version__)))
    dummy_app = QApplication(sys.argv)
    filename, _ = QFileDialog.getSaveFileName(
        None, '保存位置', 'E:/exported_history.xlsx', '*.xlsx')
    if filename:
        try:
            CurrentHistory().to_xlsx(filename)
            webbrowser.open(os.path.dirname(filename))
        except CancelledError:
            LOGGER.info('用户取消')


class TestCase(unittest.TestCase):
    def test_1(self):
        CurrentHistory().to_xlsx('E:/test/test_export.xlsx')


if __name__ == '__main__':
    main()
    # unittest.main()
