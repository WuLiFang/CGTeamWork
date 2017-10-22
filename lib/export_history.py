# coding=utf-8
"""Export task history.  """

from __future__ import print_function, unicode_literals

import logging
import os
import sys
import webbrowser

from bs4 import BeautifulSoup

from cgtwb import Current
from wlf.mp_logging import set_basic_logger
from wlf.table import RowTable

from wlf.Qt.QtWidgets import QApplication, QFileDialog

LOGGER = logging.getLogger()
if __name__ == '__main__':
    set_basic_logger()

__version__ = '0.1.1'


class CurrentHistory(RowTable):
    """Retake/Approve history of current module.  """

    def __init__(self):
        super(CurrentHistory, self).__init__()
        self.current = Current()
        self.task_module = self.current.task_module
        signs = self.current.signs
        self.infos = self.current.history_module.get_with_filter(
            ['time', 'text', 'status', '#account_id', '#task_id', 'step'],
            [['status', '=', 'Retake'], 'or', ['status', '=', 'Approve']])

        self.task_module.init_with_id([i['task_id'] for i in self.infos])

        self.task_infos = self.task_module.get([signs['name']])
        for info in self.infos:
            info.update(self.parse_html_to_xls(info['text']))
            info['name'] = self.get_task_info(info['task_id'], signs['name'])
            self.append(info)

        self.header.sort(key=lambda x:
                         (x != 'name', x != 'text', not x.startswith('ref_image'), x))

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
                link = u'http://{}/{}'.format(self.current.server_ip,
                                              i.get('src'))
                links.append(link)
        value = soup.get_text(strip=True).replace(
            'p, li { white-space: pre-wrap; }', '')

        if links:
            for index, link in enumerate(links, 1):
                xls_func = u'=HYPERLINK("{}","[{}]")'.format(
                    link, os.path.basename(link))

                ret['ref_image_{}'.format(index)] = xls_func
            value = value or '[仅有图片]'
        ret['text'] = value
        return ret


def main():
    print('{:-^50s}'.format('导出历史 v{}'.format(__version__)))
    dummy_app = QApplication(sys.argv)
    filename, _ = QFileDialog.getSaveFileName(
        None, '保存位置', 'E:/exported_history.xlsx', '*.xlsx')
    if filename:
        CurrentHistory().to_xlsx(filename)
        webbrowser.open(os.path.dirname(filename))


if __name__ == '__main__':
    main()
