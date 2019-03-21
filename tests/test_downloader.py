# -*- coding=UTF-8 -*-
"""Downloader test.  """

from __future__ import absolute_import, print_function, unicode_literals

import uuid

import pytest
from pathlib2 import Path

import cgtwq
from downloader import RemoteFile, RemoteFiles

# pylint: disable = invalid-name
cgteamwork_required = pytest.mark.skipif(
    not cgtwq.DesktopClient().is_logged_in(),
    reason='Need cgteamwork logged in')
pytestmark = []
# pylint: enable = invalid-name


@cgteamwork_required
def test_update():
    for target in ('Final', 'Submit'):
        print(RemoteFiles(target))


def test_remote_file_download(tmp_path):
    # type: (pathlib2.Path) -> None

    context1 = uuid.uuid4().hex
    remote_dir = tmp_path / 'remote'
    remote_dir.mkdir()
    local_dir = tmp_path / 'local'
    local_dir.mkdir()

    remote_file = remote_dir / "file"
    remote_file.write_bytes(context1)
    local_file = local_dir / 'file'
    RemoteFile(remote_file).download(local_file)
    assert local_file.read_bytes() == context1

    # Download again with same context
    history_dir = local_dir / RemoteFile.history_dirname
    RemoteFile(remote_file).download(local_file)
    assert local_file.read_bytes() == context1
    assert not history_dir.exists()

    # Download again with diffrent context
    context2 = uuid.uuid4().hex
    remote_file.write_bytes(context2)
    RemoteFile(remote_file).download(local_file)
    assert local_file.read_bytes() == context2
    assert history_dir.exists()
    history_files = list(history_dir.iterdir())
    assert len(history_files) == 1
    assert history_files[0].read_bytes() == context1
