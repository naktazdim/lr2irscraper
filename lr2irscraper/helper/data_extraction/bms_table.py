# -*- coding: utf-8 -*-
"""
難易度表のデータを読み取る。
すべての入出力は unicode 文字列を想定している。
(fetch.py を使って得たデータはすべて unicode 文字列に変換されている)
"""

import re
from typing import List, Union

import pandas as pd
import pyjsparser
from html.parser import HTMLParser

from lr2irscraper.helper.exceptions import ParseError


def extract_bms_table_from_html(source: str, is_overjoy=False) -> pd.DataFrame:
    """ 従来の (『次期難易度表フォーマット』に対応していない) 難易度表データを抽出する。

    Args:
        source: ソース (UTF-8 を想定)
        is_overjoy: Overjoy 表のときのみ True を指定

    Returns: 難易度表データ
             (bmsid, level, title, url1, url2, comment)
    """
    mname = extract_mname(source)
    if mname is None:
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
              .astype({"bmsid": int}))  # bmsid を数値にして返す


def extract_mname(source: str) -> Union[List[List], None]:
    """
    html のソースから <script> タグ内に書かれた var mname = [] という文を探し、その右辺を返す。
    見つからない場合は None を返す。複数ある場合は初めに見つけたものを返す。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: 難易度表データ

    """
    def nodes(tree: dict) -> List[dict]:
        ret = [tree]
        for value in tree.values():
            if isinstance(value, dict):
                ret.extend(nodes(value))
            elif isinstance(value, list):
                for node in value:
                    ret.extend(nodes(node))
        return ret

    def search_mname(tree: dict) -> Union[List[List], None]:
        for node in nodes(tree):  # 構文木のノードを一つずつ見ていって、
            if node["type"] == "VariableDeclarator" and node["id"]["name"] == "mname":  # var mname = なら
                # node["init"] が = の右辺 (Array の Array) の構文木なので、それを Python の list の list にして返す
                return [[column["value"]
                         for column in item["elements"]]
                        for item in node["init"]["elements"]]
        return None  # var mname = がみつからなければ None を返す

    for script in _extract_scripts(source):  # <script> タグの中身のうち、
        if re.search("var\s+mname\s*=", script) is None:  # var mname = がないものは
            continue  # とばして、
        # var mname = があるものについて、

        script = re.sub("(^\s*<!--|-->\s*$)", "", script)  # <!-- --> を除去して
        script_tree = pyjsparser.parse(script)  # パースして
        mname = search_mname(script_tree)  # 「var mname = [] の右辺」を探して、
        if mname is not None:  # ちゃんと得られれば
            return mname  # それを返す
    return None  # var mname = が一つも見つからなければ None を返す


def _extract_scripts(source: str) -> List[str]:
    """ html から <script> タグの中身を抽出する。

    Args:
        source: ソース

    Returns: <script> タグの中身

    """
    class ScriptExtractor(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self._in_script_tag = False
            self.script = []

        def handle_starttag(self, tag, attrs):
            if tag.lower() == "script":
                self._in_script_tag = True

        def handle_endtag(self, tag):
            if tag.lower() == "script":
                self._in_script_tag = False

        def handle_data(self, data):
            if self._in_script_tag:
                self.script.append(data)

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
