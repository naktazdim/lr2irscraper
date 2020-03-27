from typing import Union

from lr2irscraper.types import BmsMd5, Lr2Id
from lr2irscraper.helper.fetch import fetch_ranking_html, fetch_course_file
from lr2irscraper.helper.data_extraction.ranking import \
    read_bmsid_from_html, read_courseid_from_html, \
    read_course_hash_from_course_file, chart_unregistered
from lr2irscraper.helper.exceptions import UnregisteredError


def get_lr2id(bmsmd5: Union[str, BmsMd5]) -> Lr2Id:
    """BmsMd5からLr2Idを得る。

    :param bmsmd5: BmsMd5
    :return: Lr2Id
    """
    if isinstance(bmsmd5, str):
        bmsmd5 = BmsMd5(bmsmd5)
    very_large_page_number = 4294967295  # 大きいページ数を指定してランキングの表示件数を 0 件にしている
    source = fetch_ranking_html(bmsmd5, page=very_large_page_number)
    if chart_unregistered(source):
        raise UnregisteredError(bmsmd5, "bmsmd5")
    return read_bmsid_from_html(source) if bmsmd5.type == "bms" else read_courseid_from_html(source)


def get_bmsmd5(lr2id: Lr2Id) -> BmsMd5:
    """lr2id からハッシュ値を得る。コースのみ対応。
    
    :param lr2id: courseid
    :return: ハッシュ値
    """
    assert lr2id.type == "course"
    return read_course_hash_from_course_file(fetch_course_file(lr2id))