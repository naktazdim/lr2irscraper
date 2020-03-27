import requests
from urllib.parse import urlparse

_session = requests.Session()


def fetch(url: str) -> bytes:
    """指定したURL/パスにあるデータを返す。

    http://, https://, file:// のいずれかで始まる URL、ないしはローカルファイルのパスを受け取ることができる。

    :param url: URLまたはローカルファイルのパス
    :return: データ
    """
    urlparse_result = urlparse(url)

    if urlparse_result.scheme in ["http", "https"]:
        r = _session.get(url)
        r.raise_for_status()
        return r.content
    elif urlparse_result.scheme in ["file", ""]:
        return open(urlparse_result.path, "rb").read()
