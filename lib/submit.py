# -*- coding=UTF-8 -*-
"""Submit selected file.  """

import cgtwq


def main():
    cgtwq.update_setting()
    plugin_data = cgtwq.DesktopClient.get_plugin_data()

    module = cgtwq.Database(plugin_data.database).module(
        plugin_data.module, module_type=plugin_data.module_type)
    select = module.select(*plugin_data.id_list)

    select.flow.submit(plugin_data.file_path_list)


if __name__ == '__main__':
    main()
