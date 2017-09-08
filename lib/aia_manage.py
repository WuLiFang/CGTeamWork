# -*- coding=UTF-8 -*-
"""AIA check-in & check-out."""

import os
import stat
import json
import re
import datetime

import cgtwb
from wlf.files import get_encoded, copy
from wlf.message import error
from wlf.console import pause

__version__ = '0.1.0'


class CurrentAssets(cgtwb.Current):
    """Current asset selected from cgtw, mayby multiple item.  """
    fields = {'file': 'asset_task.submit_file_path',
              'aia': 'asset_task.define_iic',
              'name': 'asset.asset_name'}
    files = []
    archive_folder = 'history'

    def __init__(self):
        super(CurrentAssets, self).__init__()
        self.task_module.init_with_id(self.selected_ids)

        infos = self.task_module.get(
            [self.fields['file'], self.fields['name']])
        self.files = []
        for info in infos:
            file_info = info[self.fields['file']]
            if file_info:
                files = json.loads(file_info).get('path')
                if not files:
                    error(u'{}找不到提交文件'.format(info[self.fields['name']]))
                    raise ValueError('Submit file not found')
                for i in files:
                    try:
                        self.files.append(get_ok_file(i))
                    except NoMatchError:
                        error(u'找不到 {} 对应的ok文件'.format(i), 'NoMatch')
                        continue
            else:
                error(u'{}找不到提交文件'.format(info[self.fields['name']]))
                raise ValueError('Submit file not found')

        self._time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    def checkin(self):
        """Set file read-only and set aia status to approve the archive it.  """
        for i in self.files:
            self.archive(i)
            os.chmod(i, stat.S_IREAD)
            print('readonly', i)

        successed = self.task_module.set({self.fields['aia']: 'Approve'})
        print('checkin successed', successed)
        if not successed:
            error(u'设置aia属性不成功')

    def archive(self, filename):
        """Archive file.  """
        archive_folder = os.path.join(
            os.path.dirname(filename), self.archive_folder)
        if not os.path.exists(get_encoded(archive_folder)):
            os.mkdir(get_encoded(archive_folder))
        dest = u'{}\\'.format(os.path.join(archive_folder, self._time))
        copy(filename, dest)

    def checkout(self):
        """Set current file writable and set aia status to waiting."""
        for i in self.files:
            os.chmod(get_encoded(i), stat.S_IWRITE)
            print('writable', i)

        successed = self.task_module.set({self.fields['aia']: 'Wait'})
        print('checkout successed', successed)
        if not successed:
            error(u'设置aia属性不成功')


def get_ok_file(filename):
    """Get ok version filename.  """
    dirname = os.path.normpath(os.path.dirname(filename))
    if not re.match(r'(?i).*\\work$', dirname):
        raise NoMatchError
    ret = os.path.join(re.sub(r'(?i)\\work$', r'\ok',
                              dirname), os.path.basename(filename))
    ret = get_encoded(ret)
    if not os.path.exists(ret):
        raise NoMatchError
    return ret


class NoMatchError(Exception):
    """Indicate no match file. """

    def __str__(self):
        return 'No matched file founded.'


def main():
    """Get plugin setting from cgtw.  """

    assets = CurrentAssets()
    operation = assets.sys_module.get_argv_key('operation')
    if operation == 'checkin':
        assets.checkin()
    elif operation == 'checkout':
        assets.checkout()
    else:
        print(assets.files)
    pause()


if __name__ == '__main__':
    main()
