# -*- coding=UTF-8 -*-
"""Client status manage.  """
from __future__ import unicode_literals
import datetime
import logging

from wlf.notify import error
from wlf.timedelta import strf_timedelta, parse_timedelta

import cgtwb

__version__ = '0.1.2'
LOGGER = logging.getLogger()
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)


class CurrentItems(cgtwb.Current):
    """Current asset selected from cgtw, mayby multiple item.  """
    fields = {'name': 'shot.entity',
              'retake_record': '{0.module}.retake_record',
              'client': '{0.module}.client_status',
              'first_retake_time': '{0.module}.first_retake_time',
              'last_retake_time': '{0.module}.last_retake_time',
              'last_retake_cost': '{0.module}.last_retake_cost',
              'total_retake_cost': '{0.module}.total_retake_cost',
              'client_retake_count': '{0.module}.client_retake_count'}
    asset_task_fields = {'name': 'asset.entity'}
    l10n_dict = {
        'retake': u'✘',
        'approve': u'✔',
        None:  u'<无>',
        '':  u'<无>'
    }

    def __init__(self):
        super(CurrentItems, self).__init__()
        self.fields = dict(self.fields)
        if self.module == 'asset_task':
            self.fields.update(self.asset_task_fields)
        self.fields = {k: v.format(self) for k, v in self.fields.items()}
        LOGGER.debug('选中的id %s', self.selected_ids)
        if not self.selected_ids:
            LOGGER.error('不能获取选中id')
            raise ValueError('No selected_ids')

    def approve(self):
        """Set file read-only and set aia status to approve the archive it.  """

        self.task_module.init_with_id(self.selected_ids)
        successed = self.task_module.set({self.fields['client']: 'Approve'})
        LOGGER.info('set approve successed: %s', successed)
        if not successed:
            error(u'设置client属性不成功')
        self.set_retake_record('approve')

    def retake(self):
        """Set current file writable and set aia status to waiting."""
        self.task_module.init_with_id(self.selected_ids)
        successed = self.task_module.set({self.fields['client']: 'Retake'})
        LOGGER.info('set retake successed: %s', successed)
        if not successed:
            error(u'设置client属性不成功')
        self.set_retake_record('retake')

    def set_retake_record(self, record_name):
        """Set retake record field."""
        fields = ['retake_record', 'first_retake_time', 'last_retake_time',
                  'last_retake_cost', 'total_retake_cost', 'client_retake_count']
        cgtw_fields = [self.fields[i] for i in fields]
        self.task_module.init_with_id(self.selected_ids)

        info = self.task_module.get(cgtw_fields)
        if info is False:
            error('缺少字段, 未能记录额外信息。<br> 需要模块包含以下字段:<br>%s' %
                  '<br>'.join(fields))
            return

        for item_id in self.selected_ids:
            item_info = [i for i in info if i['id'] == item_id][0]
            data = {[i for i in self.fields if self.fields[i] == k][0]                    : v for k, v in item_info.items() if k in cgtw_fields}

            # Retake record
            if data['retake_record']:
                data['retake_record'] += '  '
            else:
                data['retake_record'] = ''
            now = datetime.datetime.now()
            strf_now = now.strftime(self.DATETIME_FORMAT)
            data['retake_record'] += '{}{}'.format(
                self.l10n(record_name), self.l10n(now))

            # Time records.
            if record_name == 'retake':
                if not data['first_retake_time']:
                    data['first_retake_time'] = strf_now
                data['last_retake_time'] = strf_now
                try:
                    data['client_retake_count'] = str(
                        int(data['client_retake_count']) + 1)
                except TypeError:
                    data['client_retake_count'] = '1'

            elif record_name == 'approve':
                last_retake_cost = now - \
                    self.parse_datetime(data['last_retake_time'])
                data['last_retake_cost'] = strf_timedelta(last_retake_cost)
                if data['total_retake_cost']:
                    total_retake_cost = parse_timedelta(
                        data['total_retake_cost']) + last_retake_cost
                else:
                    total_retake_cost = last_retake_cost
                data['total_retake_cost'] = strf_timedelta(total_retake_cost)

            self.task_module.init_with_id(item_id)
            data = {self.fields[k]: v for k, v in data.items()if v}
            LOGGER.debug('set data %s', data)
            self.task_module.set(data)

    def l10n(self, text):
        """Localization.  """
        if isinstance(text, datetime.datetime):
            return text.strftime('%x.%H')

        return self.l10n_dict.get(text, text)


def main():
    """Get plugin setting from cgtw.  """

    print('Client Manage v{}'.format(__version__))
    items = CurrentItems()
    operation = items.sys_module.get_argv_key('operation')
    if operation == 'approve':
        items.approve()
    elif operation == 'retake':
        items.retake()


if __name__ == '__main__':
    main()
