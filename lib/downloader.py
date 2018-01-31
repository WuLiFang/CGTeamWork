#! py -2.7
# -*- coding=UTF-8 -*-
"""Download submit files for selected items.
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import sys
import webbrowser

from Qt import QtCompat, QtWidgets
from Qt.QtWidgets import QRadioButton

from cgtwb import Current
from wlf.files import copy, is_same
from wlf.notify import CancelledError, progress
from wlf.path import get_unicode as u
from wlf.path import Path

SUBMIT_FILE = 1 << 0


class ServerFiles(set):
    """Server files set.  """

    def __init__(self, target=SUBMIT_FILE):
        current = Current()
        if target == SUBMIT_FILE:
            # Get from submit file path field.
            sign = current.signs['submit_file_path']
            files = set()
            all_data = current.task_module.get([sign])
            for data in all_data:
                try:
                    path = json.loads(data[sign])['path']
                except (KeyError, ValueError, TypeError):
                    continue
                if path:
                    files.update(path)
        else:
            # Get from filebox.
            files = set()
            checked_path = set()
            for id_ in progress(current.selected_ids, '获取文件框内容'):
                current.task_module.init_with_id(id_)
                data = current.task_module.get_filebox_with_filebox_id(
                    target.id)
                path = Path(data['path'])
                if path not in checked_path:
                    files.update(i for i in path.iterdir() if i.is_file())
                checked_path.add(path)

        files = (ServerFile(i) if not isinstance(i, ServerFile) else i
                 for i in list(files))
        super(ServerFiles, self).__init__(files)

    def compare_with(self, local_dir):
        for i in list(self):
            assert isinstance(i, ServerFile)
            i.is_updated = i in Path(local_dir).iterdir()

    def new_files(self):
        return sorted(i for i in self if not i.is_updated)


class ServerFile(unicode):
    """File on server.  """

    def __init__(self, path):
        super(ServerFile, self).__init__(u(path))
        self.path = path
        self.is_updated = False

    def __eq__(self, other):
        return is_same(self.path, other)


class Dialog(QtWidgets.QDialog):
    """Main dialog.  """

    def __init__(self):
        super(Dialog, self).__init__()
        QtCompat.loadUi(os.path.join(__file__, '../downloader.ui'), self)
        self.current = Current()
        self.file_sets = {}
        self._files = ServerFiles()

        # Add radio buttons.
        buttons = []
        for filebox in self.current.get_filebox(self.current.pipeline.pop()):
            button = QRadioButton(filebox.title)
            button.setObjectName(filebox.title)
            buttons.append(button)
            self.groupBox.layout().addWidget(button)
            # Set signal for button.
            button.toggled.connect(
                lambda status, target=filebox: self.on_radio_toggled(target, status))

        # Connect signals.
        self.toolButton.clicked.connect(self.ask_dir)
        self.radioButtonSubmit.toggled.connect(
            lambda status: self.on_radio_toggled(SUBMIT_FILE, status))
        self.lineEditDir.editingFinished.connect(self.autoset)
        self.checkBoxSkipSame.toggled.connect(self.update_list_widget)

        # Set config.
        self.dir = 'E:/cgtw_download'

    def update_list_widget(self):
        """Update list widget.  """

        widget = self.listWidget
        widget.clear()

        if self.checkBoxSkipSame.isChecked():
            self.files.compare_with(self.dir)
            files = sorted(self.files.new_files())
        else:
            files = sorted(self.files)

        for i in files:
            if len(i) >= 40:
                i = '...' + i[-40:]
            widget.addItem(i)
        self.labelCount.setText('{} 个文件'.format(len(files)))

    def on_radio_toggled(self, target, status):
        if status:
            if target not in self.file_sets:
                self.file_sets[target] = ServerFiles(target)
            self._files = self.file_sets[target]
            self.update_list_widget()

    def download(self):
        """Download Files.   """

        files = self.files.new_files() if self.checkBoxSkipSame.isChecked() else self.files
        try:
            for i in progress(files, '下载文件'):
                copy(i, self.dir)
            return True
        except CancelledError:
            return False

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
            webbrowser.open(self.dir)
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
