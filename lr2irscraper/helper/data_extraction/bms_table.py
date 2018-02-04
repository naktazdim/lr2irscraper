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
from urllib.parse import urljoin

from lr2irscraper.helper.exceptions import ParseError


def make_dataframe_from_mname(mname: List[List],
                              columns: List=None) -> pd.DataFrame:
    """ mname を DataFrame に変換して返す。

    Args:
        mname: extract_mname() で抽出した mname
        columns: カラム名を指定

    Returns: 難易度表データ

    """
    df = pd.DataFrame(mname)

    # カラムを指定しなかった場合の初期値
    if columns is None:
        columns = ["id", "level", "title", "bmsid", "artist", "diff", "comment"]

    # カラム数が違う場合は後ろに何かが付加されている / 後ろが削られていると仮定する
    num_columns = len(df.columns)
    if num_columns > len(columns):
        columns += ["unknown{}".format(i) for i in range(1, num_columns - len(columns) + 1)]
    elif num_columns < len(columns):
        columns = columns[:num_columns]

    df.columns = columns

    df = df.dropna(axis=0, subset=["id"])  # id が空欄になっている項目はダミーデータとみなして抜く
    df["id"] = df["id"].astype(int)  # float になっているので int に戻す

    df["level"] = df["level"].apply(_strip_tags)  # level に <font> タグがついていることがあるので抜く
    df["title"] = df["title"].apply(_strip_tags)  # title にページ内リンクがついていることがあるので抜く
    # その他のカラムのタグは除去しない

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


def column_name(url: str) -> List[str]:
    """
    旧難易度表の URL からカラム名を得る。

    Args:
        url: 難易度表の URL

    Returns: カラム名

    """
    # 気合
    default_columns = ["id", "level", "title", "bmsid", "artist", "diff", "comment"]
    a = ["id", "level", "title", "bmsid", "diff", "artist", "comment"]
    b = ["id", "level", "title", "bmsid",  "comment", "artist", "diff", "unused"]
    c = ["id", "level", "title", "ir", "ir3", "artist", "diff", "comment"]
    d = ["id", "level", "title", "bmsid", "rate", "unused", "comment"]
    e = ["id", "level", "title", "bmsid", "artist", "diff", "comment", "speed", "gauge"]
    f = ["id", "level", "title", "bmsid", "comment", "artist", "diff"]
    g = ["id", "level", "title", "bmsid", "unused1", "diff", "artist", "comment", "unused2"]
    tables = [
        (a, "10tan.web.fc2.com"),
        (a, "bmsinsane2.web.fc2.com"),
        (a, "www53.atpages.jp/merikuribms"),
        (a, "be5moti.web.fc2.com/gengaojoy"),
        (a, "hebonet.web.fc2.com/bms/lr2jun.html"),
        (a, "www.geocities.jp/bmsetc/sabun/hyou.html"),
        (a, "2nd.geocities.jp/yoshi_65c816/was/a.html"),
        (a, "vertigo_.web.fc2.com/yumerusabunhyou.html"),
        (a, "uetnosubarashikikusosabun.web.fc2.com/uet.html"),
        (b, "slash24th.web.fc2.com"),
        (c, "achusi.main.jp/overjoy"),
        (d, "sabosabun.tank.jp/record.html"),
        (e, "infinity.s60.xrea.com/bms/renda.html"),
        (f, "lunatic8192alice.web.fc2.com/ondo.html"),
        (g, "www015.upp.so-net.ne.jp/deep_throat/nanido/dp_saranan.html"),
    ]
    for columns, table_url in tables:
        if table_url in url:  # 部分一致
            return columns
    return default_columns  # どれでもなければデフォルト値


def split_url(bms_table: pd.DataFrame, bms_table_url: str):
    """
    アーティスト・差分のカラムには a タグで URL が貼られていることが多い。
    そこから URL とテキストを分離して、それぞれ別のカラムに格納する。
    それぞれのカラム名が artist, diff であると仮定している。

    Args:
        bms_table: 元の難易度表データ (DataFrame)
        bms_table_url: 難易度表の URL (差分が相対パスなことがあるので)

    Returns: URL とテキストを分離した DataFrame
        artist -> artist, url
        diff -> name_diff, url_diff
        のように分割される。「次期難易度表フォーマット」とあわせている。

    """
    href_regexp = re.compile(r"""<a\s+href=["']([^"']+?)["']>""", re.IGNORECASE)
    url_regexp = re.compile(r"https?://[!\w/:%#$&?()~.=+-]+", re.IGNORECASE)
    d = {"artist": ("artist", "url"), "diff": ("name_diff", "url_diff")}

    def extract_text(item: str):
        item = _strip_tags(item)
        item = url_regexp.sub("", item)
        return item

    def extract_url(item: str):
        m = href_regexp.search(item)
        if m is None:
            m = url_regexp.search(item)
            if m is None:
                return ""
            else:
                url = m.group(0)
        else:
            url = m.group(1)
        return urljoin(bms_table_url, url)

    for original_column, (text_column, url_column) in d.items():
        if original_column in bms_table.columns:
            orig = bms_table[original_column]
            bms_table = bms_table.drop(columns=original_column)
            bms_table[text_column] = orig.apply(extract_text)
            bms_table[url_column] = orig.apply(extract_url)

    return bms_table


def overjoy(bms_table: pd.DataFrame):
    """
    Overjoy 用特殊処理

    Args:
        bms_table: Overjoy 表の DataFrame

    Returns: 処理後の DataFrame

    """
    # データ上はレベル表記は「★+数字」 だが、一般的な「★★+数字」表記に直す
    # (もっというと <font> タグで赤文字になっているのだが、それはパースの際に抜いてある)
    bms_table["level"] = bms_table["level"].apply(lambda s: "★" + s)

    # Overjoy 表は bmsid カラムがなく、代わりに ir3 カラムにランキングページの URL が格納されている
    # そこから bmsid を抽出し、bmsid カラムを作って格納する
    bms_table["bmsid"] = bms_table["ir3"].apply(lambda s: re.match(".*bmsid=(\d+).*", s).group(1))

    # ir3 カラムは要らないので抜いてしまう。
    # ir カラムには古いランキングページ？へのリンクが入っているが、これも要らないので抜いてしまう
    bms_table.drop(columns=["ir", "ir3"])

    return bms_table


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
    return re.sub(r"<.*?>", "", source)
