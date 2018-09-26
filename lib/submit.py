# -*- coding=UTF-8 -*-
"""Submit selected file.  """

import cgtwq


def main():
    client = cgtwq.DesktopClient()
    client.connect()

    plugin_data = client.plugin.data()
    select = cgtwq.Selection.from_data(**plugin_data._asdict())
    select.flow.submit(plugin_data.file_path_list)


if __name__ == '__main__':
    main()
