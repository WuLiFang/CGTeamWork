#! py -2.7
# -*- coding=UTF-8 -*-
"""Download submit files for selected items.
"""
import os
import sys
import json

import cgtwb
from wlf.Qt import QtWidgets, QtCompat
from wlf.files import url_open, copy
from wlf.progress import Progress, CancelledError

__version__ = '0.2.0'


class Dialog(QtWidgets.QDialog):
    """Main dialog.  """

    def __init__(self):
        super(Dialog, self).__init__()
        QtCompat.loadUi(os.path.join(__file__, '../downloader.ui'), self)
        self._current = cgtwb.Current()
        if not self._current.task_module.init_with_id(self._current.selected_ids):
            raise RuntimeError('Initiate task module fail.')
        self._files = list(json.loads(i[self.submit_file_path_field])
                           for i in self._current.task_module.get([self.submit_file_path_field])
                           if i[self.submit_file_path_field])
        self._files = list(i.get('path')[0]
                           for i in self.files if i.get('path'))
        for i in self.files:
            if len(i) >= 40:
                i = '...' + i[-40:]
            self.listWidget.addItem(i)
        self.toolButton.clicked.connect(self.ask_dir)
        self.lineEditDir.editingFinished.connect(self.autoset)
        self.dir = 'E:/cgtw_download'

    def download(self):
        """Download Files.   """
        try:
            task = Progress('下载文件')
            all_num = len(self.files)
            for index, i in enumerate(self.files):
                task.set(index * 100 // all_num, os.path.basename(i))
                copy(i, self.dir)
            return True
        except CancelledError:
            return False

    @property
    def submit_file_path_field(self):
        """Field name of submit file path. """

        return 'shot_task.submit_file_path'

    @property
    def files(self):
        """Files to download.  """
        return self._files

    @property
    def dir(self):
        """Output dir.  """

        return self.lineEditDir.text() + '\\'

    @dir.setter
    def dir(self, value):
        self.lineEditDir.setText(os.path.normpath(value))

    def autoset(self):
        """Auto set dir.  """

        self.dir = self.dir

    def accept(self):
        """Override QDialog.accept().  """
        if self.download():
            url_open(self.dir, isfile=True)
            self.close()

    def ask_dir(self):
        """Show a dialog ask user.  """

        file_dialog = QtWidgets.QFileDialog()
        _dir = file_dialog.getExistingDirectory(
            dir=os.path.dirname(self.dir)
        )
        if _dir:
            self.dir = _dir


if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)
    FRAME = Dialog()
    FRAME.show()
    sys.exit(APP.exec_())
