# -*- coding=UTF-8 -*-
"""Base module for plugins develop."""

from __future__ import print_function, unicode_literals

import wlf.cgtwq

__version__ = '0.1.3'


class Current(wlf.cgtwq.CGTeamWork):
    """Warpper for cgtw.tw().sys() module. """

    sign_shot_name = 'shot.shot'

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

    def abort(self):
        """Tell cgtw abort execution.  """
        self._tw.sys().set_return_data(False)

    def is_shot(self, value):
        """Return if @value is a shot_name.  """

        return self.task_module.init_with_filter([['shot.shot', '=', value]])
