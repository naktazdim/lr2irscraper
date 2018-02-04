# -*- coding: utf-8 -*-
"""
難易度表データの取得
"""
import pandas as pd
from urllib.parse import urljoin

from lr2irscraper.helper.exceptions import ParseError
from lr2irscraper.helper.fetch import fetch
from lr2irscraper.helper.data_extraction.bms_table import *
from lr2irscraper.helper.data_extraction.bms_table_new_style import *


def get_bms_table(url: str) -> pd.DataFrame:
    """ 指定した URL から難易度表データを取得し、DataFrame として返す。

    新形式か旧形式かは自動で判定する。
    旧形式の表に関しては、発狂難易度表・Overjoy 表以外での動作は保証しない (多くはうまくいくようだが)。

    Args:
        url: URL

    Returns: 難易度表データ
             カラムは表によって異なるが、
             旧形式の場合は (id, level, title, bmsid) のカラムはほぼ常に存在する。
             新形式の場合は (md5, level) のカラムは必ず存在する (仕様)。

    """
    source = fetch(url)
    header_path = extract_header_path(source)  # まず新形式として「ヘッダ部」のパスの取得を試みる

    if header_path is None:  # なければ旧形式とみなして解釈
        mname = extract_mname(source)
        if mname is None:  # 旧形式としても解釈できなければ例外を送出して終了
            raise ParseError("Failed to detect bms table: {}".format(url))

        bms_table = make_dataframe_from_mname(mname, columns=column_name(url))
        return overjoy(bms_table) if "http://achusi.main.jp/overjoy/" in url else bms_table
    else:  # 「ヘッダ部」のパスが取得できれば新形式とみなして解釈
        header_path = urljoin(url, header_path)  # 絶対パスに変換 (header_path がもともと絶対パスのときも正しく動作する)
        header_json = fetch(header_path)
        data_path = urljoin(url, extract_data_path(header_json))
        data_json = fetch(data_path)
        return make_dataframe_from_header_and_data_json(header_json, data_json)
