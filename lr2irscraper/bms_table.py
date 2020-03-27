"""
難易度表データの取得
"""
from urllib.parse import urljoin

from lr2irscraper.helper.exceptions import ParseError
from lr2irscraper.helper.fetch import fetch
from lr2irscraper.helper.data_extraction.bms_table import *


def get_bms_table(url: str) -> pd.DataFrame:
    """ 指定した URL から難易度表データを取得し、DataFrame として返す。

    Args:
        url: URL

    Returns: 難易度表データ
    """
    source = fetch(url)
    header_path = extract_header_path(source)

    if header_path is None:
        raise ParseError("Failed to detect bms table: {}".format(url))

    header_path = urljoin(url, header_path)  # 絶対パスに変換 (header_path がもともと絶対パスのときも正しく動作する)
    header_json = fetch(header_path)
    data_path = urljoin(url, extract_data_path(header_json))
    data_json = fetch(data_path)
    return make_dataframe_from_header_and_data_json(header_json, data_json)
