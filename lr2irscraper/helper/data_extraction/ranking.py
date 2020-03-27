"""
LR2IR の search.cgi の出力からデータを読み取る。
すべての入出力は unicode 文字列を想定している。
(サーバからの生の出力は Shift-JIS なので注意。fetch.py を使って得たデータはすべて unicode 文字列に変換されている)
"""

import re

from lr2irscraper.helper.exceptions import ParseError
from lr2irscraper.types import BmsMd5, Lr2Id


def chart_unregistered(source: str) -> bool:
    """search.cgi?mode=ranking から取得した html (1 ページ分) から、未登録の譜面のデータを取得しようとしたかを返す。

    :param source: ソース (UTF-8 を想定)
    :return: ランキングデータ
    """
    return re.search("</div><!--end search--> \n"
                     "(エラーが発生しました。\n|未登録の曲です。)<br>\n"
                     "</div><!--end box--> ",
                     source) is not None


def read_player_count_from_html(source: str) -> int:
    """search.cgi?mode=ranking から取得した html (1 ページ分) から総プレイ人数を抽出する。

    :param source: ソース (UTF-8 を想定)
    :return: プレイ人数
    """
    match = re.search("  <tr><th>人数</th><td>(\d+)</td><td>\d+</td><td>[\d.]+%</td></tr>", source)
    if match is None:
        raise ParseError("Failed to detect player count")
    return int(match.group(1))


def read_bmsid_from_html(source: str) -> Lr2Id:
    """search.cgi?mode=ranking から取得した html (1 ページ分) から bmsid を抽出する。

    :param source: source: ソース (UTF-8 を想定)
    :return: bmsid
    """
    match = re.search("<a href=\"search\.cgi\?mode=editlogList&bmsid=(\d+)\">", source)
    if match is None:
        raise ParseError("Failed to detect bmsid")
    return Lr2Id("bms", int(match.group(1)))


def read_courseid_from_html(source: str) -> Lr2Id:
    """search.cgi?mode=ranking から取得した html (1 ページ分) から courseid を抽出する。

    :param source: ソース (UTF-8 を想定)
    :return: courseid
    """
    match = re.search("<a href =\"search\.cgi\?mode=downloadcourse&courseid=(\d+)\">", source)
    if match is None:
        raise ParseError("Failed to detect courseid")
    return Lr2Id("course", int(match.group(1)))


def read_course_hash_from_course_file(source: str) -> BmsMd5:
    """search.cgi?mode=downloadcourse から取得したコースファイル (course.lr2crs) からコースのハッシュ値を抽出する。

    :param source: ソース (UTF-8 を想定)
    :return: コースのハッシュ値
    """
    match = re.search("<hash>([0-9a-f]{160})</hash>", source)
    if match is None:
        raise ParseError("Failed to detect course hash")
    return BmsMd5(match.group(1))
