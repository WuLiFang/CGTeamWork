# -*- coding=UTF-8 -*-
"""Add note for retake information.  """

from __future__ import print_function, unicode_literals
import sys
import logging

from openpyxl import load_workbook

from wlf.cgtwq import Shot
from wlf.console import pause
from wlf.mp_logging import set_basic_logger
from wlf.Qt.QtWidgets import QApplication, QFileDialog
from wlf.notify import Progress, CancelledError

from cgtwb import Current

__version__ = '0.1.1'

LOGGER = logging.getLogger()


if __name__ == '__main__':
    set_basic_logger()


class XLSXParser(object):
    """Read info from xlsx file.  """

    def __init__(self, filename):
        self.current = Current()
        self.workbook = load_workbook(filename)
        self.worksheet = self.workbook.get_active_sheet()
        result = {}
        self.is_shot = self.current.is_shot

        rows = tuple(self.worksheet.rows)
        task = Progress('分析表格', total=len(rows))
        for row in rows:
            shot, note = self.parse_row(row)
            task.step(shot)
            if shot is None:
                continue
            if result.has_key(shot):
                result[shot] += note
            else:
                result[shot] = note

        self.result = result

    def parse_row(self, row):
        """Parse single row to find shot note.  """

        shot = None
        note_lines = []

        note_begin = False
        for cell in row:
            value = cell.value
            if not value:
                continue
            elif note_begin:
                note_lines.append(value)
            elif self.is_shot(value):
                LOGGER.debug('Found shot: %s', value)
                shot = value
                note_begin = True

        note = '\n'.join(note_lines)
        return (shot, note)


class Noter(object):
    """Note adding helper.  """

    def __init__(self):
        super(Noter, self).__init__()
        self.shot_note = {}
        self.current = Current()
        pipeline = self.current.pipeline
        if pipeline and len(pipeline) == 1:
            self.pipeline = list(pipeline)[0]
        else:
            # TODO: Ask pipeline
            self.pipeline = None
        LOGGER.info('备注将添加至流程: %s', self.pipeline)

    def parse_file(self, filename):
        """Read info from file.  """

        if filename.endswith('.xlsx'):
            self.shot_note = XLSXParser(filename).result
        else:
            raise NotImplementedError('Not supported file format.')

    def execute(self):
        """Add notes for self.shot_info.  """

        shot_names = sorted(self.shot_note.keys())
        task = Progress('添加note', total=len(shot_names))

        for shot_name in shot_names:
            note = self.shot_note[shot_name]
            if note:
                shot = Shot(shot_name, pipeline=self.pipeline)
                if shot.add_note(note, distinct=True):
                    LOGGER.info('%s:添加备注', shot_name)
                else:
                    LOGGER.info('%s:已存在相同备注,跳过', shot_name)
            task.step(shot_name)


def main():
    print('{:-^50}'.format('导入备注 v{}'.format(__version__)))
    dummy = QApplication(sys.argv)
    noter = Noter()

    filename, _ = QFileDialog.getOpenFileName(
        None, caption='选择要读取的文件…', filter='*.xlsx')

    if not filename:
        return

    try:
        noter.parse_file(filename)
        noter.execute()
        pause()
    except CancelledError:
        LOGGER.info('用户取消')


if __name__ == '__main__':
    main()
