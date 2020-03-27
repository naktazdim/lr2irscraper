"""
LR2IR の search.cgi や getrankingxml.cgi などの出力からデータを読み取る。
すべての入出力は unicode 文字列を想定している。
(サーバからの生の出力は Shift-JIS なので注意。fetch.py を使って得たデータはすべて unicode 文字列に変換されている)
"""

import re
import xml.etree.ElementTree

import pandas as pd


from lr2irscraper.helper.exceptions import ParseError


def extract_ranking_from_xml(source: str) -> pd.DataFrame:
    """ getrankingxml.cgi から取得したデータからランキングデータを抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: ランキングデータ
             (id, name, clear, notes, combo, pg, gr, minbp)
             clear は 1-5 の数値で、FAILED, EASY, CLEAR, HARD, FULLCOMBO に対応する。
             ★FULLCOMBO の情報は取得できない (FULLCOMBO と同じく 5 になる)。

    """
    columns = ["id", "name", "clear", "notes", "combo", "pg", "gr", "minbp"]
    # うち、整数値のもの
    ints = ["id", "clear", "notes", "combo", "pg", "gr", "minbp"]

    match = re.search(r'(<ranking>.*?</ranking>)', source, re.DOTALL)  # <ranking> タグの中身のみを対象とする
    if match is None:
        raise ParseError
    source = match.group(0)

    # パースして dict を生成
    try:
        records = [
            [child.find(key).text for key in columns]
            for child in xml.etree.ElementTree.fromstring(source)
        ]
    except xml.etree.ElementTree.ParseError:
        raise ParseError

    return (
        pd.DataFrame(records, columns=columns)
          .astype({column: int for column in ints})
    )


def chart_unregistered(source: str) -> bool:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) から、未登録の譜面のデータを取得しようとしたかを返す。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: ランキングデータ

    """
    return re.search("</div><!--end search--> \n"
                     "(エラーが発生しました。\n|未登録の曲です。)<br>\n"
                     "</div><!--end box--> ",
                     source) is not None


def read_player_count_from_html(source: str) -> int:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) から総プレイ人数を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: プレイ人数

    """
    match = re.search("  <tr><th>人数</th><td>(\d+)</td><td>\d+</td><td>[\d.]+%</td></tr>", source)
    if match is None:
        raise ParseError("Failed to detect player count")
    return int(match.group(1))


def read_bmsid_from_html(source: str) -> int:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) から bmsid を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: bmsid

    """
    match = re.search("<a href=\"search\.cgi\?mode=editlogList&bmsid=(\d+)\">", source)
    if match is None:
        raise ParseError("Failed to detect bmsid")
    return int(match.group(1))


def read_courseid_from_html(source: str) -> int:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) から courseid を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: courseid

    """
    match = re.search("<a href =\"search\.cgi\?mode=downloadcourse&courseid=(\d+)\">", source)
    if match is None:
        raise ParseError("Failed to detect courseid")
    return int(match.group(1))


def read_course_hash_from_course_file(source: str) -> str:
    """ search.cgi?mode=downloadcourse から取得したコースファイル (course.lr2crs) からコースのハッシュ値を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: コースのハッシュ値

    """
    match = re.search("<hash>([0-9a-f]{160})</hash>", source)
    if match is None:
        raise ParseError("Failed to detect course hash")
    return match.group(1)
