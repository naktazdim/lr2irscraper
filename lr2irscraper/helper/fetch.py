"""
LR2IR の search.cgi や getrankingxml.cgi などの生出力を取得する。
ただし、元の Shift JIS ではなく unicode 文字列を返す。
"""
# -*- coding: utf-8 -*-
import requests
from typing import Union
_session = requests.Session()


def fetch(url: str, encoding: str = "auto") -> str:
    """ 指定した URL からデータを得る。

    Args:
        url: URL
        encoding: エンコーディング ("auto" の場合は自動判定)

    Returns: データ

    """
    r = _session.get(url)
    r.encoding = r.apparent_encoding if encoding == "auto" else encoding
    return r.text


def fetch_ranking_xml(hash_value: str) -> str:
    """ ハッシュを指定して、getrankingxml.cgi からランキングデータの xml データを取得する。

    Args:
        hash_value: bms の場合は 32 桁、コースの場合は 160 桁の 16 進数値

    Returns: 生の xml

    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                  "/2/getrankingxml.cgi?id=1&songmd5={}".format(hash_value))


def fetch_ranking_html(id_or_hash: Union[int, str], mode: str, page: int) -> str:
    """ ID を指定して、search.cgi からランキングページの html データを 1 ページ取得する。

    Args:
        id_or_hash: bmsid, courseid, ハッシュ値のいずれかを指定
        mode: "bmsid", "courseid", "hash" のいずれかを指定
        page: ページ番号

    Returns: 生の html (1 ページ分)

    """
    if mode in ["bmsid", "courseid"]:
        key_value = "{}={}".format(mode, id_or_hash)
    elif mode == "hash":
        key_value = "bmsmd5={}".format(id_or_hash)

    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                 "/search.cgi?mode=ranking&{}&page={}".format(key_value, page))


def fetch_course_file(courseid: int) -> str:
    """ courseid を指定して、コースファイルを取得する。

    Args:
        courseid: コースの ID

    Returns: 「コースファイル」 (xml)

    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                  "/search.cgi?mode=downloadcourse&courseid={}".format(courseid))
