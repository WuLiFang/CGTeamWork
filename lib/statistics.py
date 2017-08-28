#! py -2.7
# -*- coding=UTF-8 -*-
"""Create statistics sheet for CGTeamWork.

>>> Database('proj_big', 'asset_task').info().generate_page('e:/test/test.html')
"""
import os
import sys
import json
import datetime

from PySide.QtGui import QFileDialog, QApplication, QDialog, QErrorMessage

from ui_statistics import Ui_Dialog

from wlf.cgtwq import CGTeamWork
from wlf.files import get_encoded, url_open

__version__ = '0.4.2'


class Database(CGTeamWork):
    """CGteamwork database. """

    artist_field = 'asset_task.artist'

    def __init__(self, database=None, module=None, since=None):
        super(Database, self).__init__()
        self.database = database or self._tw.sys().get_sys_database()
        self.module = module or self._tw.sys().get_sys_module()
        self.task_module.init_with_filter([])
        self._artists = list(i for i in self.task_module.get_distinct_with_filter(
            'asset_task.artist', []) if i)
        self._since = since

    def info(self):
        """Return all needed info as a object. """
        ret = {}
        for artist in self.artists:
            ret[artist] = self.artist(artist).info(since=self._since)
        return Info(ret)

    @property
    def artists(self):
        """Artists in this database.  """
        return self._artists

    def artist(self, name):
        """Return artists has match @name.  """
        info = self.task_module.get_with_filter(AssetTask.fields.values(),
                                                [[self.artist_field, '=', name]])
        return Artist(info)

    def serialize(self):
        """Return serialized information.  """
        return self.info()


class Artist(object):
    """Artist on CGteamwork.  """
    _tasks = []

    def __init__(self, tasks=None):
        super(Artist, self).__init__()
        if tasks:
            self._tasks = AssetTasks(tasks)

    @property
    def tasks(self):
        """Tasks assigned to this artist. """
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        self._tasks = AssetTasks(value)

    def level_count(self, since=None):
        """Return count for each level.  """
        ret = {}
        ret['finished'] = self.finished_tasks(
            since=since).level_count(div=True)
        ret['working'] = self.working_tasks().level_count(div=True)
        return ret

    def finished_tasks(self, since=None):
        """Return finished tasks for this artist since @since given time.  """

        ret = AssetTasks(
            task for task in self.tasks if task.is_newer_than(since))
        return ret

    def working_tasks(self):
        """Return working tasks for this artist.  """
        ret = AssetTasks(task for task in self.tasks if not task.is_approved)
        return ret

    def serialize(self):
        """Return serialized information.  """
        return self.level_count()

    def info(self, since=None):
        """Return all needed info. """
        return self.level_count(since=since)


class AssetTasks(list):
    """Multiple asset task."""

    def __init__(self, tasks):
        super(AssetTasks, self).__init__()
        for task in tasks:
            if not isinstance(task, AssetTask):
                task = AssetTask(task)
            self.append(task)
        self._pipelines = set(i.pipeline for i in self)

    def level_count(self, div=False):
        """Return count for each level. divide by pipeline if @div.  """
        ret = {}
        if div:
            for pipeline in self.pipelines:
                ret[pipeline] = self.pipeline_tasks(pipeline).level_count()
        else:
            for task in self:
                level = task.level
                if not level:
                    level = u'~'
                level = level.upper()
                ret.setdefault(level, 0)
                ret[level] += 1
        return ret

    def pipeline_tasks(self, pipeline):
        """Return match pipeline tasks.   """
        return AssetTasks(i for i in self if i.pipeline == pipeline)

    @property
    def pipelines(self):
        """Return task pipeline self contained.  """
        return self._pipelines


class AssetTask(object):
    """A asset task. """
    fields = {'level': 'asset.define_jbg',
              'finish_time': 'asset_task.finish_time',
              'submit_time': 'asset_task.last_submit_time',
              'name': 'asset.asset_name',
              'cn_name': 'asset.cn_name',
              'status': 'asset_task.status',
              'pipeline': 'asset_task.pipeline'}

    timef = '%Y-%m-%d %H:%M:%S'

    def __init__(self, info):
        super(AssetTask, self).__init__()
        assert isinstance(info, dict), 'Expected dict, got {}'.format(info)
        self._info = info

    @property
    def name(self):
        """Return name of this task"""
        return self._info[self.fields['name']]

    @property
    def cn_name(self):
        """Return cn——name of this task"""
        return self._info[self.fields['cn_name']]

    @property
    def level(self):
        """Return diffcult level of this task"""
        return self._info[self.fields['level']]

    @property
    def pipeline(self):
        """Return pipeline of this task"""
        return self._info[self.fields['pipeline']]

    @property
    def is_approved(self):
        """return if this task has been approved.  """
        return self._info[self.fields['status']] == 'Approve'

    @property
    def finish_time(self):
        """Task finish time in time struct. """
        str_time = self._info[self.fields['finish_time']]
        if str_time:
            return datetime.datetime.strptime(str_time, self.timef)

    def is_newer_than(self, date):
        """Return if newer than @date.  """

        assert isinstance(
            date, datetime.datetime), 'Expected datetime.datetime, got {}'.format(date)
        if self.is_approved:
            return self.finish_time >= date


def indent(text, num=4):
    """Indent text by line.  """
    return '\n'.join(list(' ' * num + i for i in text.split('\n')))


class Info(dict):
    """Data info for asset tasks."""
    path = None

    def __init__(self, info=None):
        if isinstance(info, dict) or not info:
            dict.__init__(self, info)
        elif isinstance(info, (str, unicode))\
                and os.path.exists(get_encoded(info)):
            with open(info) as f:
                dict.__init__(self, json.load(f))
            self.path = info
        else:
            raise ValueError('Need dict or json path to initilize.')

    def generate_page(self, path):
        """Create html page form info.  """

        _classes = ['artist', 'status', 'pipeline', 'level', 'amount']
        translate = {'working': u'制作中', 'finished': u'已通过'}

        def _rows_generator(key, value, depth=0):
            ret = []
            key = translate.get(key) or key

            if not value:
                pass
            elif isinstance(value, dict):
                for k, v in value.items():
                    ret.extend(_rows_generator(k, v, depth=depth + 1))
                if ret:
                    template = u'\n<td class="{class_name}", rowspan={0}>{1}</td>{2}'
                    ret[0] = template.format(
                        len(ret), key, ret[0], class_name=_classes[depth])
                    ret = [indent(i) for i in ret]
            else:
                template = u'\n<td class="{class1}">{0}</td><td class="{class2}">{1}</td>'
                ret = [indent(template.format(
                    key, value, class1=_classes[depth], class2=_classes[depth + 1]))]
            return ret

        rows = []
        row_template = u'''<tr>
{}
</tr>'''
        for k, v in self.items():
            if not v:
                continue
            if isinstance(v, Artist):
                v = v.serialize()
            new_rows = list(indent(row_template.format(i))
                            for i in _rows_generator(k, v))
            rows.extend(new_rows)

        body = '\n'.join(rows)

        template = u'''<body>
<table>
    <tr>
        <th>姓名</th>
        <th>状态</th>
        <th>工序</th>
        <th>难度级别</th>
        <th>数量</th>
    </tr>
{}</table>
</body>'''
        body = template.format(body)
        with open(os.path.join(__file__, '../statistics.head.html')) as f:
            head = f.read()
        with open(get_encoded(path), 'w') as f:
            f.write(get_encoded(head + body, 'UTF-8'))
        self.write(os.path.splitext(path)[0] + '.json')

        return path

    def write(self, path=None):
        """Write this info to disk.  """
        path = path or self.path
        with open(get_encoded(path), 'w') as f:
            json.dump(self, f, cls=InfoEncoder, indent=4)


class InfoEncoder(json.JSONEncoder):
    """JSONEncoder for Info."""

    def default(self, o):
        try:
            return o.serialize()
        except AttributeError:
            return json.JSONEncoder.default(self, o)


class Dialog(QDialog, Ui_Dialog):
    """Dialog as cgteamwork plugin.  """

    def __init__(self):
        def _actions():
            self.actionPath.triggered.connect(self.ask_path)
        super(Dialog, self).__init__()
        self.setupUi(self)
        _actions()

    def ask_path(self):
        """Show a dialog ask config['NUKE'].  """

        dialog = QFileDialog()
        filename, selected_filter = dialog.getSaveFileName(
            filter='*.html')
        selected_filter = selected_filter[1:]
        if filename:
            if not filename.endswith(selected_filter):
                filename += selected_filter
            self.lineEdit.setText(filename)

    def accept(self):
        """Overrride QDialog accept.  """
        path = self.lineEdit.text()
        date = self.dateTimeEdit.dateTime().toPython()
        try:
            info = Database(since=date).info()
            info.generate_page(path)
            url_open(path, isfile=True)
            self.close()
        except NoMatchError:
            QErrorMessage(self).showMessage(u'无匹配条目\n{}')


class NoMatchError(Exception):
    """Indecate no match item on cgtw.  """

    def __str__(self):
        return u'no match item founded. '


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    FRAME = Dialog()
    FRAME.show()
    sys.exit(APP.exec_())
