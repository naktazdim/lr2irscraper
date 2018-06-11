# -*- coding: utf-8 -*-
"""
次期難易度表フォーマットのデータを読み取る。
http://bmsnormal2.syuriken.jp/bms_dtmanager.html
"""
import json
from typing import Union
from collections import OrderedDict

from html.parser import HTMLParser
import pandas as pd
from pandas.api.types import CategoricalDtype


def extract_header_path(source: str) -> Union[str, None]:
    """
    難易度表ページの html ソースから、「ヘッダ部」のパスを読み取る。
    見つからない場合 (「次期難易度表フォーマット」のページではない場合) は None を返す。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: 「ヘッダ部」のパス

    """
    class HeaderPathExtractor(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.header_path = None

        def handle_starttag(self, tag, attrs):
            if tag.lower() == "meta":
                attrs_dict = dict(attrs)
                if attrs_dict.get("name") == "bmstable":
                    self.header_path = attrs_dict.get("content")

    header_path_extractor = HeaderPathExtractor()
    header_path_extractor.feed(source)
    return header_path_extractor.header_path


def extract_data_path(source: str) -> str:
    """
    難易度表ページ「ヘッダ部」の JSON データから、「データ部」のパスを読み取る。

    Args:
        source: ソース (UTF-8 を想定)

    Returns: 「データ部」のパス

    """
    return json.loads(source)["data_url"]


def make_dataframe_from_header_and_data_json(header_json: str, data_json: str) -> pd.DataFrame:
    """
    次期難易度表フォーマットのデータを DataFrame として返す。

    "level" カラムは Categorical, 他のカラムはすべて文字列 (object 型) とする。
    表記レベルの先頭にはシンボルを付加する (たとえば "▼0")。
    欠損値は空文字列とする。

    Args:
        header_json: 「ヘッダ部」の JSON データ
        data_json: 「データ部」の JSON データ

    Returns:

    """
    header = json.loads(header_json, object_pairs_hook=OrderedDict)
    data = json.loads(data_json, object_pairs_hook=OrderedDict)

    if len(data) == 0:
        # 空の場合も、仕様上の必須カラムは用意しておく。"level" カラムは存在しないと以下の処理で困る
        table = pd.DataFrame(columns=["md5", "level"], dtype=object)
    else:
        table = pd.DataFrame.from_dict(data, dtype=object).fillna("")

    tag = header.get("tag") or header["symbol"]
    level_order = header.get("level_order") or table["level"].drop_duplicates().values
    level_order = list(map(str, level_order))  # 仕様では Array(String | Integer) となっている。str に統一しておく。

    return (
        table
        .astype({"level": str})  # 仕様では str なのだが、int が入っていることがある (例: 新 Overjoy) ので str に統一しておく
        .astype({"level": CategoricalDtype(categories=level_order, ordered=True)})
        .assign(level=lambda df: df["level"].cat.rename_categories([tag + level for level in level_order]))
    )
