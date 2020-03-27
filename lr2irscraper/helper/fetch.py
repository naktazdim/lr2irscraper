"""
LR2IR の search.cgi や getrankingxml.cgi などの生出力を取得する。
ただし、元の Shift JIS ではなく unicode 文字列を返す。
"""
import requests

from lr2irscraper.types import BmsMd5, Lr2Id

_session = requests.Session()


def fetch(url: str, encoding: str = "auto") -> str:
    """指定した URL からデータを得る。

    :param url: URL
    :param encoding: エンコーディング ("auto" の場合は自動判定)
    :return: データ
    """
    r = _session.get(url)
    r.raise_for_status()
    r.encoding = r.apparent_encoding if encoding == "auto" else encoding
    return r.text


def fetch_ranking_xml(bmsmd5: BmsMd5) -> str:
    """ハッシュを指定して、getrankingxml.cgi からランキングデータの xml データを取得する。

    :param bmsmd5: bmsmd5
    :return: 生の xml
    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                 "/2/getrankingxml.cgi?id=1&songmd5={}".format(bmsmd5),
                 encoding="cp932")


def fetch_ranking_html(bmsmd5: BmsMd5, page: int) -> str:
    """ID を指定して、search.cgi からランキングページの html データを 1 ページ取得する。

    :param bmsmd5: bmsmd5
    :param page: ページ番号
    :return: 生の html (1 ページ分)
    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                 "/search.cgi?mode=ranking&bmsmd5={}&page={}".format(bmsmd5, page),
                 encoding="cp932")


def fetch_course_file(courseid: Lr2Id) -> str:
    """courseid を指定して、コースファイルを取得する。

    :param courseid: courseid: コースの ID
    :return: 「コースファイル」 (xml)
    """
    return fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                 "/search.cgi?mode=downloadcourse&courseid={}".format(courseid.id),
                 encoding="cp932")
