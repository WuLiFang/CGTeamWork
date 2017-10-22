# -*- coding=UTF-8 -*-
"""Base module for plugins develop."""

from __future__ import print_function, unicode_literals
import logging

from wlf.cgtwq import CGTeamWork

__version__ = '0.1.6'
LOGGER = logging.getLogger('cgtwb')


class Current(CGTeamWork):
    """Warpper for cgtw.tw().sys() module. """

    instance = None
    pipeline_shots = None
    _task_names = None
    _pipeline = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = super(Current, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super(Current, self).__init__()
        self.task_module.init_with_id(self.selected_ids)

    def __len__(self):
        return len(self.selected_ids)

    @property
    def database(self):
        """Current database. """
        return self._tw.sys().get_sys_database()

    @property
    def module(self):
        """Current module.  """
        return self._tw.sys().get_sys_module()

    @property
    def selected_ids(self):
        """Current selected id list.  """
        return self._tw.sys().get_sys_id()

    @property
    def selected_link_ids(self):
        """Current selected id list in link window.  """
        return self._tw.sys().get_sys_link_id()

    @property
    def files(self):
        """Current selected file list in file window.  """
        return self._tw.sys().get_sys_file()

    @property
    def folder(self):
        """Current selected folder in file window.  """
        return self._tw.sys().get_sys_folder()

    @property
    def plantform(self):
        """Current operating system.  """
        return self._tw.sys().get_sys_os()

    @property
    def account(self):
        """Current account.  """
        return self._tw.sys().get_account()

    @property
    def account_id(self):
        """Current account id.  """
        return self._tw.sys().get_account_id()

    @property
    def token(self):
        """Current token.  """
        return self._tw.sys().get_token()

    @property
    def server_ip(self):
        """Current server ip.  """
        return self._tw.sys().get_server_ip()

    @property
    def task_names(self):
        """List of current selected task.  """

        if self._task_names is None:
            self._task_names = [i[self.signs['name']]
                                for i in self.task_module.get([self.signs['name']])]
        return self._task_names

    @property
    def pipeline(self):
        """Pipeline set of current selected task.  """

        if self._pipeline is None:
            pipeline = set()
            infos = self.task_module.get([self.SIGNS['pipeline']])
            if infos:
                _ = [pipeline.add(i[self.SIGNS['pipeline']]) for i in infos]
            self._pipeline = pipeline
        return self._pipeline

    def abort(self):
        """Tell cgtw abort execution.  """
        self._tw.sys().set_return_data(False)

    def is_shot(self, value):
        """Return if @value is a shot_name.  """

        ret = None

        if self.pipeline and self.pipeline_shots is None:
            shots = set()
            filters = []
            for i in self.pipeline:
                filters.append([self.SIGNS['pipeline'], '=', i])
                filters.append('or')
            filters = filters[:-1]
            initiadted = self.task_module.init_with_filter(filters)
            if initiadted:
                infos = self.task_module.get([self.SIGNS['shot']])
                _ = [shots.add(i[self.SIGNS['shot']]) for i in infos]
            else:
                LOGGER.warning(
                    'Can not initiate with pipeline: %s', self.pipeline)
            self.pipeline_shots = shots

        if self.pipeline_shots:
            ret = value in self.pipeline_shots

        if ret is None:
            ret = self.task_module.init_with_filter(
                [[self.SIGNS['shot'], '=', value]])

        return ret
