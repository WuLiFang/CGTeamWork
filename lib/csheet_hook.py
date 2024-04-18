# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Any

from cgtwq.desktop import new_client
from wulifang._util import capture_exception
import logging
import requests

_LOGGER = logging.getLogger(__name__)


class _GQLClient:
    def __init__(self, url, login, password):
        # type: (Text, Text, Text) -> None
        self._url = url
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._session.trust_env = False  # ignore system proxy setting

    def execute(self, operation_name, query, variables):
        # type: (Text,Text, dict[str, Any]) -> dict[str, Any]

        _LOGGER.info("send: %s: %s" % (operation_name, variables))
        resp = self._session.post(  # type: ignore
            self._url,
            json=dict(operationName=operation_name, query=query, variables=variables),
            auth=(self._login, self._password),
        )  # type: requests.Response
        if resp.status_code != 200:  # type: ignore
            raise RuntimeError(
                "POST %s: status: %s: %s" % (self._url, operation_name, resp.status_code)  # type: ignore
            )
        res = resp.json()  # type: ignore
        _LOGGER.info("receive: %s" % (res,))
        if "errors" in res:
            raise RuntimeError(
                "%s: gql error: %s: %s"
                % (self._url, operation_name, [i["message"] for i in res["errors"]])  # type: ignore
            )
        return res["data"]  # type: ignore


def main():
    client = new_client()
    ctx = client.plugin.context()
    argv = ctx.argv
    if len(argv) < 4:
        plugin = client.plugin.get(ctx.plugin_id)
        argv = plugin.argv()
        argv.add("serverURL", "必填，色板服务器根地址。")
        argv.add("login", "必填，使用的色板账号。")
        argv.add("password", "必填，使用的色板密码。")
        argv.add("instanceCode", "选填，当前 CGT 实例的编号。")
        raw_argv = argv.encode()
        if raw_argv != plugin.raw_argv:
            plugin.raw_argv = raw_argv
            client.plugin.save(plugin, only_fields=["argv"])
            _LOGGER.info("update plugin arguments")

    serverURL = argv["serverURL"]
    if not serverURL:
        raise RuntimeError("serverURL is required")
    if serverURL.endswith("/"):
        serverURL = serverURL[:-1]
    login = argv["login"]
    if not login:
        raise RuntimeError("login is required")
    password = argv["password"]
    if not password:
        raise RuntimeError("password is required")
    instanceCode = argv["instanceCode"]
    sourceURLs = [
        "com.wlf-studio.cgteamwork.object://%s/%s/%s/%s/%s"
        % (instanceCode, ctx.database, ctx.module, ctx.module_type, id)
        for id in ctx.id_list
    ]
    _LOGGER.info("sourceURLs: %s", sourceURLs)
    if not sourceURLs:
        return

    gql = _GQLClient(serverURL + "/api", login, password)
    gql.execute(
        "cgteamworkHookImportCollection",
        """
mutation cgteamworkHookImportCollection($input: ImportCollectionInput!) {
  importCollection(input: $input) {
    updatedCount
  }
}
        """,
        {"input": {"data": [{"url": i} for i in sourceURLs]}},
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with capture_exception():
        main()
