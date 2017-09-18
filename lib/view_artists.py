# -*- coding=UTF-8 -*-
"""View artist of selected shot.  """

from cgtwb import Current
from wlf.notify import message_box

__version__ = '0.1.1'


class CurrentShotTasks(Current):
    """Current selected shot tasks.  """
    fields = {
        'shot': 'shot.shot',
        'artist': 'shot_task.artist',
        'pipeline': 'shot_task.pipeline',
    }

    def __init__(self):
        super(CurrentShotTasks, self).__init__()

        self.task_module.init_with_id(self.selected_ids)
        infos = self.task_module.get(self.fields.values())
        shots = [i[self.fields['shot']] for i in infos]
        shots_filters = [[self.fields['shot'], '=', i] for i in shots]
        shots_filter = [shots_filters[0]]
        for i in shots_filters[1:]:
            shots_filter.append('or')
            shots_filter.append(i)
        initiated = self.task_module.init_with_filter(shots_filter)
        if not initiated:
            raise ValueError(shots, shots_filter)
        infos = self.task_module.get(self.fields.values())
        self._shots_info = {}
        for info in infos:
            shot = info[self.fields['shot']]
            self._shots_info.setdefault(shot, {})
            self._shots_info[shot][info[self.fields['pipeline']]] = info.get(
                self.fields['artist'])
        print(self._shots_info)

    def show_artists(self):
        """Show artist through message box.  """
        msg = ''
        for shot, info in self._shots_info.items():
            msg += u'{}\n'.format(shot)
            msg += u'\n'.join([u'{}: {}'.format(pipeline, info[pipeline])
                               for pipeline in info])
            msg += u'\n\n'
        if len(msg) < 300:
            message_box(msg)
        else:
            message_box(u'制作人员信息见detail', msg)


if __name__ == '__main__':
    CurrentShotTasks().show_artists()
