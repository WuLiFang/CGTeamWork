# -*- coding=UTF-8 -*-
"""Submit selected file.  """

import cgtwb

__version__ = '0.1.1'

if __name__ == '__main__':
    CUR = cgtwb.Current()
    CUR.task_module.init_with_id(CUR.selected_ids)
    CUR.submit(CUR.files, note=u'自cgtw提交')
