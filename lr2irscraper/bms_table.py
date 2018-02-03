# -*- coding: utf-8 -*-
"""
難易度表データの取得
"""
import pandas as pd

from lr2irscraper.helper.fetch import fetch
from lr2irscraper.helper.data_extraction.bms_table import extract_bms_table_from_html


def get_bms_table(url: str, is_overjoy: bool=None) -> pd.DataFrame:
    """ 指定した URL から従来の (『次期難易度表フォーマット』に対応していない) 難易度表データを取得する。

    発狂難易度表・Overjoy 表以外の表での動作は保証しない (半数程度はうまくいくようだが)。

    Args:
        url: URL
        is_overjoy: Overjoy 表かどうか (指定しなければ自動判定するが、うまくいかない場合は明示的に指定)

    Returns: 難易度表データ
             (bmsid, level, title, url1, url2, comment)

    """
    if is_overjoy is None:
        is_overjoy = ("http://achusi.main.jp/overjoy/" in url)
    return extract_bms_table_from_html(fetch(url), is_overjoy=is_overjoy)
