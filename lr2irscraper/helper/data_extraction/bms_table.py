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


def make_dataframe_from_mname(mname: List[List],
                              is_overjoy: bool=False,
                              columns: List=None) -> pd.DataFrame:
    """ mname を DataFrame に変換して返す。

    Args:
        mname: extract_mname() で抽出した mname
        is_overjoy: Overjoy 表のときのみ True を指定
        columns: カラム名を指定、省略した場合は (bmsid, level, title, url1, url2, comment)

    Returns: 難易度表データ

    """
    df = pd.DataFrame(mname)

    # データからカラム名を取得できないので、適当に決める
    if columns is None:
        if is_overjoy:
            columns = ["id", "level", "title", "ir", "ir3", "original_artist", "sabun", "comment"]
        else:
            # 基本構成 (多くはこれ)
            columns = ["id", "level", "title", "bmsid", "original_artist", "sabun", "comment"]

            # カラム数が 7 のときは上記構成そのままと仮定する (本当はたまに入れ替わっていたりするが)
            # カラム数が違う場合は後ろに何かが付加されている / 後ろが削られていると仮定する
            num_columns = len(df.columns)
            if num_columns > 7:
                columns += ["unknown{}".format(i) for i in range(1, num_columns - 6)]
            elif num_columns < 7:
                columns = columns[:num_columns]

    df.columns = columns

    df["level"] = df["level"].apply(_strip_tags)  # level に <font> タグがついていることがあるので抜く
    df["title"] = df["title"].apply(_strip_tags)  # title にページ内リンクがついていることがあるので抜く
    df = df.drop("id", axis=1)  # 最初の列は落とす (表示部で使用されている内部 ID のようなものが入っている)

    # Overjoy 表は構成が違うので特殊処理
    if is_overjoy:
        # Overjoy 表の場合は bmsid そのものではなくランキングページの URL が格納されている
        # そこから bmsid を抽出し、"bmsid" カラムに格納する
        df["bmsid"] = df["ir3"].apply(lambda s: re.match(".*bmsid=(\d+).*", s).group(1))

        # ランキングページの URL そのものはいらないので抜いてしまう
        df = df.drop(columns=["ir", "ir3"])

        # データ上はレベル表記は「赤文字で ★+数字」 だが、一般的な「★★+数字」表記に直す
        # 「赤文字で」の部分は上で抜いてある
        df["level"] = df["level"].apply(lambda s: "★" + s)

        # 「基本構成」と同じ順に戻しておく
        df = df[["level", "title", "bmsid", "original_artist", "sabun", "comment"]]

    return df


def extract_mname(source: str) -> Union[List[List], None]:
    """
    html のソースから <script> タグ内に書かれた var mname = [] という文を探し、その右辺を返す。
    見つからない場合は None を返す。複数ある場合は初めに見つけたものを返す。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: 難易度表データ

    """
    def nodes(tree: dict) -> List[dict]:
        if tree is None:  #
            return []
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
                return [[column["value"] if column is not None else None
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
