#! py -2.7
# -*- coding=UTF-8 -*-
"""Download submit files for selected items.
"""
from __future__ import absolute_import, print_function, unicode_literals

import errno
import glob
import hashlib
import json
import logging
import os
import webbrowser

from Qt import QtCompat
from Qt.QtWidgets import QDialog, QFileDialog, QRadioButton

import cgtwq
from wlf.config import Config as BaseConfig
from wlf.fileutil import copy
from wlf.path import Path
from wlf.progress import CancelledError, progress
from wlf.uitools import main_show_dialog

SUBMIT_FILE = 1 << 0


class Config(BaseConfig):
    """Downloader config.  """

    default = {'OUTPUT_DIR': 'E:/cgtw_download'}
    path = os.path.expanduser(u'~/.wlf/.downloader.json')


CONFIG = Config()
LOGGER = logging.getLogger(__name__)


class RemoteFiles(set):
    """Server files set.  """

    def __init__(self, target=SUBMIT_FILE):
        select = cgtwq.DesktopClient().selection()
        files = set()
        if target == SUBMIT_FILE:
            # Get from submit file path field.]

            for i in select['submit_file_path']:
                try:
                    pathlist = json.loads(i)['file_path']
                    if isinstance(pathlist, list):
                        files.update(pathlist)
                except (KeyError, ValueError, TypeError):
                    LOGGER.warning('Can not parse: %s', i)
                    continue
        else:
            # Get from filebox.
            checked = set()
            for entry in progress(select.to_entries(), '获取文件框内容'):
                assert isinstance(entry, cgtwq.Entry)
                filebox = entry.filebox.from_id(target.id)
                path = Path(filebox.path)
                for rule in filebox.rule:
                    key = (path, rule)
                    if key in checked:
                        continue
                    files.update(i for i in path.glob(rule) if i.is_file())
                    checked.add(key)

        files = (RemoteFile(i) if not isinstance(i, RemoteFile) else i
                 for i in list(files))
        super(RemoteFiles, self).__init__(files)

    def compare_with(self, local_dir):
        """Check if file already downloaded to @local_dir.  """

        _local_dir = Path(local_dir)
        is_dir_exists = _local_dir.exists()
        existed = [get_weak_filehash(i) for i in _local_dir.iterdir()]
        for i in progress(list(self), '比较文件修改日期'):
            assert isinstance(i, RemoteFile)
            i.is_updated = is_dir_exists and get_weak_filehash(i) in existed

    def new_files(self):
        """Not downloaded files.  """

        return sorted(i for i in self if not i.is_updated)


class RemoteFile(unicode):
    """File on server.  """

    history_dirname = '_history'

    def __init__(self, *_args):
        self.is_updated = False

    def download(self, dest, is_skip_same=True):
        """Download file to dest.  """

        _dest = Path(dest)
        if not _dest.exists():
            copy(self, _dest)

            return

        dest_hash = get_weak_filehash(_dest)

        if get_weak_filehash(self) != dest_hash:
            history_folder = Path(_dest.parent / self.history_dirname)
            history_folder.mkdir(parents=True, exist_ok=True)
            backup_file = (history_folder /
                           _dest.with_suffix(
                               '.{}{}'.format(dest_hash[:8],
                                              _dest.suffix)).name)
            try:
                _dest.rename(backup_file)
            except OSError as ex:
                if ex.errno != errno.EEXIST:
                    raise ex
        elif is_skip_same:
            return

        copy(self, _dest)


def get_weak_filehash(path):
    """Fast weak hash.  """

    h = hashlib.sha1()
    _path = Path(path)
    stat = _path.stat()
    h.update('{0:s}\n\n{1:.4f}\n\n{2:d}'.format(
        _path.name, stat.st_mtime, stat.st_size))
    return h.hexdigest()


class Dialog(QDialog):
    """Main dialog.  """

    def __init__(self):
        super(Dialog, self).__init__()
        QtCompat.loadUi(os.path.join(__file__, '../downloader.ui'), self)
        self.file_sets = {}
        self._files = RemoteFiles()

        # Recover from config.
        self.dir = CONFIG['OUTPUT_DIR']

        # Setup radio buttons.
        self.radioButtonSubmit.toggled.connect(
            lambda status: self.on_radio_toggled(SUBMIT_FILE, status))
        select = cgtwq.DesktopClient().selection()
        pipeline = select.module.database.pipeline.filter(
            cgtwq.Filter('entity_name', select['pipeline'][0]))[0]
        for filebox in (select.module
                        .database
                        .filebox
                        .filter(cgtwq.Filter('#pipeline_id', pipeline.id))):
            button = QRadioButton(filebox.title)
            button.setObjectName(filebox.title)
            button.toggled.connect(
                lambda status, target=filebox: self.on_radio_toggled(target, status))
            self.groupBox.layout().addWidget(button)

        # Connect signals.
        self.toolButton.clicked.connect(self.ask_dir)
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
        if not status:
            return

        if target not in self.file_sets:
            self.file_sets[target] = RemoteFiles(target)
        self._files = self.file_sets[target]
        self.update_list_widget()

    def download(self):
        """Download Files.   """

        is_skip_same = self.checkBoxSkipSame.isChecked()
        for i in progress(self.files, '下载文件', parent=self):
            i.download(Path(self.dir) / Path(i).name,
                       is_skip_same=is_skip_same)

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

        try:
            self.download()
            webbrowser.open(self.dir)
            self.close()
        except CancelledError:
            pass

    def ask_dir(self):
        """Show a dialog ask user.  """

        file_dialog = QFileDialog()
        _dir = file_dialog.getExistingDirectory(
            dir=os.path.dirname(self.dir)
        )
        if _dir:
            self.dir = _dir


def main():
    cgtwq.DesktopClient().connect()
    main_show_dialog(Dialog)


if __name__ == '__main__':
    main()
