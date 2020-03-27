"""
bmsid/courseid とハッシュ値との相互変換
"""
from typing import Tuple

from lr2irscraper.helper.fetch import *
from lr2irscraper.helper.data_extraction.ranking import *
from lr2irscraper.helper.exceptions import UnregisteredError
from lr2irscraper.types import BmsMd5, Lr2Id


def hash_to_id(bmsmd5: BmsMd5) -> Lr2Id:
    """BmsMd5からLr2Idを得る。

    :param bmsmd5: BmsMd5
    :return: Lr2Id
    """
    if bmsmd5.type == "bms":
        return hash_to_bmsid(bmsmd5)
    elif bmsmd5.type == "course":
        return hash_to_courseid(bmsmd5)


def hash_to_bmsid(bmsmd5: BmsMd5) -> Lr2Id:
    """BMS のハッシュ値から bmsid を得る。

    :param bmsmd5: ハッシュ値
    :return: bmsid
    """
    try:
        very_large_page_number = 4294967295  # 大きいページ数を指定してランキングの表示件数を 0 件にしている
        return read_bmsid_from_html(fetch_ranking_html(bmsmd5, page=very_large_page_number))
    except ParseError:
        raise UnregisteredError(bmsmd5, "hash")


def hash_to_courseid(bmsmd5: BmsMd5) -> Lr2Id:
    """コースのハッシュ値から courseid を得る。

    :param bmsmd5: ハッシュ値
    :return: courseid
    """
    try:
        very_large_page_number = 4294967295  # 大きいページ数を指定してランキングの表示件数を 0 件にしている
        return read_courseid_from_html(fetch_ranking_html(bmsmd5, mode="hash", page=very_large_page_number))
    except ParseError:
        raise UnregisteredError(bmsmd5, "hash")


# def bmsid_to_hash(self, bmsid: int) -> str:
#     """ bmsid から BMS のハッシュ値を得る……といいたいが、簡便に得る手段がない
#
#     Args:
#         bmsid: bmsid
#
#     Returns: ハッシュ値
#
#     """
#     raise NotImplementedError


def courseid_to_hash(courseid: Lr2Id) -> BmsMd5:
    """courseid からコースのハッシュ値を得る。
    
    :param courseid: courseid
    :return: ハッシュ値
    """
    assert courseid.type == "course"
    try:
        return read_course_hash_from_course_file(fetch_course_file(courseid))
    except ParseError:
        raise UnregisteredError(courseid, "courseid")