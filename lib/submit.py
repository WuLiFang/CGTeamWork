# -*- coding=UTF-8 -*-
"""Submit selected file.  """

import cgtwb

if __name__ == '__main__':
    CUR = cgtwb.Current()
    print(CUR.selected_ids, 1)
    CUR.task_module.init_with_id(CUR.selected_ids)
    CUR.submit(CUR.files, note=u'自cgtw提交')
    input()
