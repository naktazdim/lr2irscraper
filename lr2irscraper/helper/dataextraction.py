# -*- coding: utf-8 -*-
"""
LR2IR の search.cgi や getrankingxml.cgi などの出力からデータを読み取る。
すべての入出力は unicode 文字列を想定している。
(サーバからの生の出力は Shift-JIS なので注意。fetch.py を使って得たデータはすべて unicode 文字列に変換されている)
"""

import re
import xml.etree.ElementTree
from collections import OrderedDict
from html.parser import HTMLParser
from ast import literal_eval

import pandas as pd

from lr2irscraper.helper.exceptions import ParseError


def extract_ranking_from_xml(source: str) -> pd.DataFrame:
    """ getrankingxml.cgi から取得したデータからランキングデータを抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: ランキングデータ

    """
    columns = ["name", "clear", "notes", "combo", "pg", "gr", "minbp"]

    match = re.search(r'(<ranking>.*?</ranking>)', source, re.DOTALL)  # <ranking> タグの中身のみを対象とする
    if match is None:
        raise ParseError
    source = match.group(0)

    # パースして dict を生成
    try:
        data_dict = {
            int(child.find("id").text):
                OrderedDict([(key, child.find(key).text) for key in columns])
            for child in xml.etree.ElementTree.fromstring(source)
        }
    except xml.etree.ElementTree.ParseError:
        raise ParseError

    return (
        pd.DataFrame.from_dict(data_dict, orient="index")
                    .astype({column: int for column in ["clear", "notes", "combo", "pg", "gr", "minbp"]})
                    .sort_index()
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
    columns = ["rank", "playerid", "name", "sp_dan", "dp_dan", "clear", "dj_level",
               "score", "max_score", "score_percentage", "combo", "notes", "minbp", "pg", "gr", "gd", "bd", "pr",
               "gauge_option", "random_option", "input", "body", "comment"]
    # うち、整数値のものとカテゴリ変数のもの
    ints = ["rank", "playerid", "score", "max_score", "combo", "notes", "minbp", "pg", "gr", "gd", "bd", "pr"]
    categories = ["sp_dan", "dp_dan", "clear", "dj_level", "gauge_option", "random_option", "input", "body"]
    
    lines = source.split("\n")

    try:
        header_line_number = lines.index(header)  # ヘッダ行が何行目かを取得
    except ValueError:  # もし見つからなければ
        raise ParseError

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
          .astype({column: "category" for column in categories})
          .set_index("playerid")
          .sort_index()
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
        raise ParseError
    return int(match.group(1))


def read_bmsid_from_html(source: str) -> int:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) から bmsid を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: bmsid

    """
    match = re.search("<a href=\"search\.cgi\?mode=editlogList&bmsid=(\d+)\">", source)
    if match is None:
        raise ParseError
    return int(match.group(1))


def read_courseid_from_html(source: str) -> int:
    """ search.cgi?mode=ranking から取得した html (1 ページ分) から courseid を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: courseid

    """
    match = re.search("<a href =\"search\.cgi\?mode=downloadcourse&courseid=(\d+)\">", source)
    if match is None:
        raise ParseError
    return int(match.group(1))


def read_course_hash_from_course_file(source: str) -> str:
    """ search.cgi?mode=downloadcourse から取得したコースファイル (course.lr2crs) からコースのハッシュ値を抽出する。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: コースのハッシュ値

    """
    match = re.search("<hash>([0-9a-f]{160})</hash>", source)
    if match is None:
        raise ParseError
    return match.group(1)


def extract_bms_table_from_html(source: str, is_overjoy=False) -> pd.DataFrame:
    """ 従来の (『次期難易度表フォーマット』に対応していない) 難易度表データを抽出する。

    Args:
        source: ソース (UTF-8 を想定)
        is_overjoy: Overjoy 表のときのみ True を指定

    Returns: 難易度表データ
             index: bmsid
             columns: level, title, url1, url2, comment
    """
    """
    JavaScript を真面目にパースするのはちょっと大変なので以下のような方針。
    発狂難易度表や Overjoy 表では上手くいくが、他の表では半数程度しか成功しない。
         1. <script> タグの中身を抽出
         2. var mname = [ を探す
         3. ]; を ([] の対応を考えずに総当りで) 探す。[] 内が literal_eval() で解釈できるまで続ける

    literal_eval() はあくまで Python のリテラルを解釈するものなので、
    「JavaScript としては正しいが Python としては正しくない」ようなものが入っているとうまくいかない。
    実際にあるのは「カンマの連続」「コメントアウト」「全角スペース (!)」

    ちなみに、json.loads() でパースしようとするのはいわゆる末尾カンマのせいで全くうまく行かない。
    コメントアウトや全角スペースも JSON では許容されていないのであまり意味がない。
    """
    script = _extract_scripts(source)

    mname_with_garbage = re.search("var\s+?mname\s*?=\s*?(\[.*)", script, re.DOTALL).group(1)  # var mname = [ 以下末尾まで
    mname = None
    for match in re.finditer("\](?=;)", mname_with_garbage):  # ]; を探して
        try:
            mname = literal_eval(mname_with_garbage[: match.end()])  # [] 内を literal_eval() でパースしてみる
            break  # できたら抜ける
        except SyntaxError:
            continue  # パースできなければ次の ]; を探す
    if mname is None:  # 最後まで literal_eval が成功しなければエラー
        raise ParseError

    # Overjoy 表は構成が異なるので特殊処理
    if is_overjoy:
        mname =\
            [[record[0],
              "★" + _strip_tags(record[1]),  # "<font color='red'>★1</font>" → "★★1"
              _strip_tags(record[2]),  # 譜面名にページ内リンク <a name=""> が付加されていることがあるので除去
              re.match(".*bmsid=(\d+).*", record[4]).group(1),  # LR2IR へのリンクが必ず貼られているのでそこから bmsid を抽出
              record[5], record[6], record[7]]
             for record in mname]

    # DataFrame に変換して返す
    columns = ["", "level", "title", "bmsid", "url1", "url2", "comment"]
    return (pd.DataFrame(mname, columns=columns)  # DataFrame にして
              .drop("", axis=1)  # 最初の列を落として
              .astype({"bmsid": int})  # bmsid を数値にして
              .set_index("bmsid")  # bmsid を index として
              .sort_index())  # ソートして返す


def _extract_scripts(source: str) -> str:
    """ html から <script> タグの中身を抽出する。

    Args:
        source: ソース

    Returns: <script> タグの中身

    """
    class ScriptExtractor(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self._in_script_tag = False
            self.script = ""

        def handle_starttag(self, tag, attrs):
            if tag.lower() == "script":
                self._in_script_tag = True

        def handle_endtag(self, tag):
            if tag.lower() == "script":
                self._in_script_tag = False

        def handle_data(self, data):
            if self._in_script_tag:
                self.script += data + "\n"

    script_extractor = ScriptExtractor()
    script_extractor.feed(source)
    return script_extractor.script


def _strip_tags(source: str) -> str:
    """ html からタグを除去したものを返す。

    Args:
        source: ソース

    Returns: タグを抜いたテキスト

    """
    class TagStripper(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.text = ""

        def handle_data(self, data):
            self.text += data

    tag_stripper = TagStripper()
    tag_stripper.feed(source)
    return tag_stripper.text
