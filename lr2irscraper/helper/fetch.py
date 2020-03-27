"""
LR2IR の search.cgi や getrankingxml.cgi などの生出力を取得する。
ただし、元の Shift JIS ではなく unicode 文字列を返す。
"""
from typing import Dict, Any
import requests
from urllib.parse import urlparse
import json

from lr2irscraper.types import BmsMd5, Lr2Id

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


def fetch_ranking_html(bmsmd5: BmsMd5, page: int) -> str:
    """ID を指定して、search.cgi からランキングページの html データを 1 ページ取得する。

    :param bmsmd5: bmsmd5
    :param page: ページ番号
    :return: 生の html (1 ページ分)
    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                 "/search.cgi?mode=ranking&bmsmd5={}&page={}".format(bmsmd5, page)).decode("cp932")


def fetch_course_file(courseid: Lr2Id) -> str:
    """courseid を指定して、コースファイルを取得する。

    :param courseid: courseid: コースの ID
    :return: 「コースファイル」 (xml)
    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                 "/search.cgi?mode=downloadcourse&courseid={}".format(courseid.id)).decode("cp932")


def fetch_bmstable_json(url: str) -> Dict[str, Any]:
    """次期難易度表フォーマットのJSONファイル (headerまたはdata) を取得し、dictにして返す。

    :param url: URL
    :return: dict
    """
    # 仕様で UTF-8 と決まっている。"utf-8" だと BOM あり UTF-8 が読めない。 utf-8-sig は BOM ありもなしもどちらも読める
    return json.loads(fetch(url).decode("utf-8-sig"))
