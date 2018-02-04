# -*- coding: utf-8 -*-
"""
LR2IR の search.cgi や getrankingxml.cgi などの出力からデータを読み取る。
すべての入出力は unicode 文字列を想定している。
(サーバからの生の出力は Shift-JIS なので注意。fetch.py を使って得たデータはすべて unicode 文字列に変換されている)
"""

import re
import xml.etree.ElementTree

import pandas as pd
from pandas.api.types import CategoricalDtype


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


def extract_ranking_from_html(source: str) -> pd.DataFrame:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) からランキングデータを抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: ランキングデータ

    """
    # ヘッダ行
    header = ("  <tr><th>順位</th><th>プレイヤー</th><th>段位</th><th>クリア</th><th>ランク</th><th>スコア</th>"
              "<th>コンボ</th><th>B+P</th><th>PG</th><th>GR</th><th>GD</th><th>BD</th><th>PR</th><th>OP</th>"
              "<th>OP</th><th>INPUT</th><th>本体</th></tr>")
    # データ行 (1 レコードあたり 2 行) の正規表現
    data_regexp = re.compile(
        "  <tr><td rowspan=\"2\" align=\"center\">(\d+?)</td>"
        "<td><a href=\"search\.cgi\?mode=mypage&playerid=(\d+?)\">(.*?)</a></td><td>(.*?)/(.*?)</td>"
        "<td>(.*?)</td><td>(.*?)</td><td>(\d+?)/(\d+?)\(([\d.]+?%)\)</td><td>(\d+?)/(\d+?)</td>"
        "<td>(\d+?)</td><td>(\d+?)</td><td>(\d+?)</td><td>(\d+?)</td><td>(\d+?)</td><td>(\d+?)</td>"
        "<td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(LR2)</td></tr>\n"
        "  <tr><td colspan = \"16\" class=\"gray\">(.*?)</td></tr>")
    # 上記の正規表現のグループ (括弧) がそれぞれ順に以下の値に対応する
    columns = ["rank", "id", "name", "sp_dan", "dp_dan", "clear", "dj_level",
               "score", "max_score", "score_percentage", "combo", "notes", "minbp", "pg", "gr", "gd", "bd", "pr",
               "gauge_option", "random_option", "input", "body", "comment"]
    # うち、整数値のものとカテゴリ変数のもの
    ints = ["rank", "id", "score", "max_score", "combo", "notes", "minbp", "pg", "gr", "gd", "bd", "pr"]
    categories = {
        "sp_dan": CategoricalDtype(
                categories=["-",
                            "☆01", "☆02", "☆03", "☆04", "☆05", "☆06", "☆07", "☆08", "☆09", "☆10",
                            "★01", "★02", "★03", "★04", "★05", "★06", "★07", "★08", "★09", "★10", "★★", "(^^)"],
                ordered=True),
        "dp_dan": CategoricalDtype(
                categories=["-",
                            "☆01", "☆02", "☆03", "☆04", "☆05", "☆06", "☆07", "☆08", "☆09", "☆10",
                            "★01", "★02", "★03", "★04", "★05", "★06", "★07", "★08", "★09", "★10", "★★", "(^^)"],
                ordered=True),
        "clear": CategoricalDtype(
                # 先頭の "" は内部コードを xml 側の数値とあわせるためのダミー
                categories=["", "FAILED", "EASY", "CLEAR", "HARD", "FULLCOMBO", "★FULLCOMBO"],
                ordered=True),
        "dj_level": CategoricalDtype(
                categories=["F", "E", "D", "C", "B", "A", "AA", "AAA"],
                ordered=True),
        "gauge_option": CategoricalDtype(
                categories=["易", "普", "難", "死", "PA", "GA"],
                ordered=False),  # "GA" があるので ordered とは言えない
        "input": CategoricalDtype(
                categories=["BM", "KB", "MIDI"],
                ordered=False),
        "body": CategoricalDtype(
                categories=["LR2"],
                ordered=False),
    }

    lines = source.split("\n")

    try:
        header_line_number = lines.index(header)  # ヘッダ行が何行目かを取得
    except ValueError:  # もし見つからなければ
        raise ParseError("Failed to detect ranking data")

    # 気合いでパース
    records = []
    for i in range(header_line_number + 1, len(lines), 2):  # ヘッダ行の次の行から
        match = data_regexp.match("\n".join(lines[i: i + 2]))  # 2 行ずつ読んで上記の正規表現を適用する
        if match is None:  # マッチしなければ
            break  # そこで終了
        records.append(match.groups())
    
    return (
        pd.DataFrame(records, columns=columns)
          .astype({column: int for column in ints})
          .astype({column: category for column, category in categories.items()})
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
