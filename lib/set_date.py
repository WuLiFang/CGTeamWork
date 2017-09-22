# -*- coding=UTF-8 -*-
"""Set date with record.  """
import os
import sys
import datetime

from wlf.Qt import QtCompat
from wlf.Qt.QtWidgets import QDialog, QApplication, QTableWidgetItem

import cgtwb

__version__ = '0.1.1'


class CurrentItems(cgtwb.Current):
    """Current asset selected from cgtw, mayby multiple item.  """
    shot_task_fields = {'name': 'shot.shot',
                        'start_date': 'shot_task.start_date',
                        'end_date': 'shot_task.end_date',
                        'deadline': 'shot_task.dead_line',
                        'first_submit': 'shot_task.first_submit_time',
                        'last_submit': 'shot_task.last_submit_time',
                        'finish_time': 'shot_task.finish_time'}
    asset_task_fields = {'name': 'asset.asset_name',
                         'start_date': 'asset_task.start_date',
                         'end_date': 'asset_task.end_date',
                         'deadline': 'asset_task.dead_line',
                         'first_submit': 'asset_task.first_submit_time',
                         'last_submit': 'asset_task.last_submit_time',
                         'finish_time': 'asset_task.finish_time'}
    fields = None
    l10n_dict = {
        'start_date': u'开始日期',
        'end_date': u'预计完成日期',
        'deadline': u'规定完成日期',
        'first_submit': u'首次提交',
        'last_submit': u'最后提交',
        'finish_time': u'完成时间',
        None:  u'<无>',
        '':  u'<无>'
    }

    def __init__(self):
        super(CurrentItems, self).__init__()
        if self.module == 'shot_task':
            self.fields = self.shot_task_fields
        elif self.module == 'asset_task':
            self.fields = self.asset_task_fields
        else:
            raise NotImplementedError('Module %s not supported' % self.module)

    def set_dates(self, dates):
        """Set item dates with note.  """
        note = u'''<style>
    * {
        font-family: 微软雅黑,SimHei
    }
    h1{
        font-size: 1.5em;
        text-weight: bold;
    }
    h2{
        font-size: 1.2em;
        text-weight: bold;
    }
    table{
        font-size: 1.5em;
        text-align: center;
    }
</style>'''
        note += u'<h1>日期变更</h1><table>'
        data_dict = {self.fields[k]: self.l10n(v) for k, v in dates.items()}
        _tr = u'<!--{1}--><tr><td>{0}</td><td>-><td><td>{1}</td><tr>'
        note += u'\n'.join(sorted([_tr.format(self.l10n(k), self.l10n(v))
                                   for k, v in dates.items()]))
        note += '</table>'
        remark_fields = ['first_submit', 'last_submit', 'finish_time']
        for item_id in self.selected_ids:
            self.task_module.init_with_id(item_id)
            self.task_module.set(data_dict)
            info = self.task_module.get(
                [self.fields[i] for i in remark_fields])[0]
            remark = u'<br>'.join([u'{}: {}'.format(
                self.l10n(field),
                self.l10n(info.get(self.fields[field]))) for field in remark_fields])
            self.add_note(
                u'{}<hr><h2>当前状态:</h2>{}'.format(note, remark))

    def get_info(self):
        """Get information. """
        initialted = self.task_module.init_with_id(self.selected_ids)
        if not initialted:
            raise RuntimeError('Can not initiate task module.  ')
        return self.task_module.get(self.fields.values())

    def l10n(self, text):
        """Localization.  """
        if isinstance(text, datetime.date):
            return text.strftime('%Y-%m-%d')
        return self.l10n_dict.get(text, text)


class Dialog(QDialog):
    """Dialog as cgteamwork plugin.  """

    def __init__(self):
        def _signals():
            self.checkBoxStartDate.stateChanged.connect(self.dateEditStartDate)
        super(Dialog, self).__init__()
        self._items = CurrentItems()
        self.dates = {}

        QtCompat.loadUi(os.path.abspath(
            os.path.join(__file__, '../set_date.ui')), self)

        today = datetime.date.today()
        self.dateEditStartDate.setDate(today)
        self.dateEditEndDate.setDate(today + datetime.timedelta(days=5))
        self.dateEditDeadline.setDate(today + datetime.timedelta(days=7))
        self.labelCount.setText(u'{}个条目'.format(len(self._items)))
        self.labelVersion.setText(u'v{}'.format(__version__))

        def _table():
            table = self.tableWidget
            table.setRowCount(len(self._items))
            fields = self._items.fields
            columns = [fields['name'], fields['first_submit'],
                       fields['last_submit'], fields['finish_time']]
            for row, info in enumerate(self._items.get_info()):
                for column, key in enumerate(columns):
                    item = QTableWidgetItem(info.get(key))
                    table.setItem(row, column, item)
        _table()

    def accept(self):
        """Overrride QDialog accept.  """
        edits = {
            self.dateEditStartDate: 'start_date',
            self.dateEditEndDate: 'end_date',
            self.dateEditDeadline: 'deadline'
        }
        dates = {field: edit.date().toPython()
                 for edit, field in edits.items() if edit.isEnabled()}

        self._items.set_dates(dates)
        self.close()


def main():
    """Script entry.  """
    app = QApplication(sys.argv)
    frame = Dialog()
    frame.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
