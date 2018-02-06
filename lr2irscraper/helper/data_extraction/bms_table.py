# -*- coding: utf-8 -*-
"""
難易度表のデータを読み取る。
すべての入出力は unicode 文字列を想定している。
(fetch.py を使って得たデータはすべて unicode 文字列に変換されている)
"""

import re
from typing import List, Union

import numpy as np
import pandas as pd
import pyjsparser
from html.parser import HTMLParser
from urllib.parse import urljoin

from lr2irscraper.helper.exceptions import ParseError


def extract_mname(source: str) -> Union[pd.DataFrame, None]:
    """
    html のソースから <script> タグ内に書かれた var mname = [] という文を探し、その右辺を DataFrame の形で返す。
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

    def search_mname_node(tree: dict) -> Union[dict, None]:
        for node in nodes(tree):  # 構文木のノードを一つずつ見ていって、
            if node["type"] == "VariableDeclarator" and node["id"]["name"] == "mname":  # var mname = なら
                # node["init"] が = の右辺 (Array の Array) の構文木
                return node["init"]
        return None  # var mname = がみつからなければ None を返す

    def make_mname_dataframe(mname_node: dict) -> pd.DataFrame:
        df = pd.DataFrame(
            [[item["value"] if item is not None else None
              for item in column["elements"]]
             for column in mname_node["elements"]]
        )

        # pyjsparser の時点で js の整数リテラルが Python の float になってしまっている
        # mname の各行の先頭の要素は整数もしくは null である
        # null のものはダミーデータとみなして抜いてしまい、あとは int に戻して返す
        df = df.dropna(axis=0, subset=[0])
        df[0] = df[0].astype(int)
        return df

    for script in _extract_scripts(source):  # <script> タグの中身のうち、
        if re.search("var\s+mname\s*=", script) is None:  # var mname = がないものは
            continue  # とばして、
        # var mname = があるものについて、

        script = re.sub("(^\s*<!--|-->\s*$)", "", script)  # <!-- --> を除去して
        script_tree = pyjsparser.parse(script)  # パースして
        mname_node = search_mname_node(script_tree)  # 「var mname = [] (の右辺)」を探して、
        if mname_node is None:  # なければ
            continue  # 次の <script> タグへ
        return make_mname_dataframe(mname_node)  # あれば DataFrame に変換して返す
    return None  # var mname = が一つも見つからなければ None を返す


def postprocess(mname: pd.DataFrame, bms_table_url: str):
    """
    読みやすいように諸々の後処理をする。

    Args:
        mname: extract_mname() の返り値
        bms_table_url: 表の URL

    Returns: 後処理をしたあとの DataFrame

    """
    # まずはカラム名を付加
    add_column_name(mname, bms_table_url)

    # 未使用カラムを除去
    if "unused" in mname.columns:
        mname = mname.drop(columns="unused")

    # アーティスト・差分カラムからそれぞれの URL とテキストを分離
    mname = split_url(mname, bms_table_url)

    # id カラムはウェブサイト上で表示する際の処理に使われているだけなので抜いてしまう
    mname = mname.drop(columns="id")

    # level に <font> タグが、title にページ内リンクがついていることがあるのでそれぞれ抜く
    mname[["level", "title"]] = mname[["level", "title"]].applymap(_strip_tags)

    # Overjoy 表は少し構成が特殊なので専用処理
    if "achusi.main.jp/overjoy" in bms_table_url:
        mname = overjoy(mname)

    # title と lr2_bmsid がともに空の行はダミーデータとみなして除去
    # (片方だけ抜けていることはしばしばある)
    mname = mname[~((mname[["title", "lr2_bmsid"]] == "").all(axis=1))]

    # 並べ替え
    # level, title, lr2_bmsid, artist, url, name_diff, url_diff, comment, その他 の順
    column_order_base = ["level", "title", "lr2_bmsid", "artist", "url", "name_diff", "url_diff", "comment"]
    column_order = (
        [column for column in column_order_base if column in mname.columns]
        + [column for column in mname.columns if column not in column_order_base]
    )

    # \r が入った項目があると .to_csv() で問題が生じる (クォートされない) ので、\r は除去する
    # 具体的には発狂難易度表の ★4 Lieselotte [INSANE] で comment に \r が単体で入っていることへの対策
    # \n であればクォートしてくれて read_csv() では読み込めるようだが、面倒なので一緒に削ってしまう
    mname = mname.applymap(lambda s: re.sub(r"[\r\n]", " ", s) if isinstance(s, str) else s)

    return mname[column_order]


def column_name(url: str) -> List[str]:
    """
    旧難易度表の URL からカラム名を得る。

    Args:
        url: 難易度表の URL

    Returns: カラム名

    """
    # 気合
    default_columns = ["id", "level", "title", "lr2_bmsid", "artist", "diff", "comment"]
    a = ["id", "level", "title", "lr2_bmsid", "diff", "artist", "comment"]
    b = ["id", "level", "title", "lr2_bmsid",  "comment", "artist", "diff", "unused"]
    c = ["id", "level", "title", "ir", "ir3", "artist", "diff", "comment"]
    d = ["id", "level", "title", "lr2_bmsid", "rate", "unused", "comment"]
    e = ["id", "level", "title", "lr2_bmsid", "artist", "diff", "comment", "speed", "gauge"]
    f = ["id", "level", "title", "lr2_bmsid", "comment", "artist", "diff"]
    g = ["id", "level", "title", "lr2_bmsid", "unused", "diff", "artist", "comment", "unused"]
    h = ["id", "level", "title", "lr2_bmsid", "artist", "diff", "original_level", "comment"]
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
        (h, "bmsohaka.web.fc2.com/cemetery.html")
    ]
    for columns, table_url in tables:
        if table_url in url:  # 部分一致
            return columns
    return default_columns  # どれでもなければデフォルト値


def add_column_name(mname: pd.DataFrame, bms_table_url: str):
    """
    URL からカラム名を判定し、mname に付加する。mname そのものを変更する。

    Args:
        mname: extract_mname() の返り値
        bms_table_url: 難易度表の URL

    """
    # とりあえず自動判定
    columns = column_name(bms_table_url)

    # もしカラム数が違う場合は後ろに何かが付加されている / 後ろが削られていると仮定する
    num_columns = len(mname.columns)
    if num_columns > len(columns):
        columns += ["unknown{}".format(i) for i in range(1, num_columns - len(columns) + 1)]
    elif num_columns < len(columns):
        columns = columns[:num_columns]

    mname.columns = columns

    return mname


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
    # (もっというと <font> タグで赤文字になっているのだが、それは事前に抜いてあるものとする)
    bms_table["level"] = bms_table["level"].apply(lambda s: "★" + s)

    # Overjoy 表は bmsid カラムがなく、代わりに ir3 カラムにランキングページの URL が格納されている
    # そこから bmsid を抽出し、bmsid カラムを作って格納する
    bms_table["lr2_bmsid"] = bms_table["ir3"].apply(lambda s: re.match(".*bmsid=(\d+).*", s).group(1))

    # ir3 カラムは要らないので抜いてしまう。
    # ir カラムには古いランキングページ？へのリンクが入っているが、これも要らないので抜いてしまう
    bms_table = bms_table.drop(columns=["ir", "ir3"])

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
