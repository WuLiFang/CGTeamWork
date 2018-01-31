#! py -2.7
# -*- coding=UTF-8 -*-
"""Download submit files for selected items.
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import webbrowser

from Qt import QtCompat
from Qt.QtWidgets import QDialog, QFileDialog, QRadioButton

from cgtwb import Current
from wlf.files import copy, is_same
from wlf.notify import CancelledError, progress
from wlf.path import get_unicode as u
from wlf.path import Path, PurePath
from wlf.uitools import main_show_dialog
from wlf.config import Config as BaseConfig

SUBMIT_FILE = 1 << 0


class Config(BaseConfig):
    """Downloader config.  """

    default = {'OUTPUT_DIR': 'E:/cgtw_download'}
    path = os.path.expanduser(u'~/.wlf/.downloader.json')


CONFIG = Config()


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
        """Check if file already dowanloaded to @local_dir.  """

        path = Path(local_dir)
        is_path_exists = path.exists()
        for i in progress(list(self), '比较文件修改日期'):
            assert isinstance(i, ServerFile)
            i.is_updated = is_path_exists and i in path.iterdir()

    def new_files(self):
        """Not dowanloaded files.  """

        return sorted(i for i in self if not i.is_updated)


class ServerFile(unicode):
    """File on server.  """

    def __init__(self, path):
        super(ServerFile, self).__init__(u(path))
        self.path = path
        self.is_updated = False

    def __eq__(self, other):
        if PurePath(other).name != PurePath(self.path).name:
            return False
        return is_same(self.path, other)


class Dialog(QDialog):
    """Main dialog.  """

    def __init__(self):
        super(Dialog, self).__init__()
        QtCompat.loadUi(os.path.join(__file__, '../downloader.ui'), self)
        self.current = Current()
        self.file_sets = {}
        self._files = ServerFiles()

        # Recover from config.
        self.dir = CONFIG['OUTPUT_DIR']

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
        path = os.path.normpath(value)
        self.lineEditDir.setText(path)
        CONFIG['OUTPUT_DIR'] = path

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

        file_dialog = QFileDialog()
        _dir = file_dialog.getExistingDirectory(
            dir=os.path.dirname(self.dir)
        )
        if _dir:
            self.dir = _dir


if __name__ == '__main__':
    main_show_dialog(Dialog)
