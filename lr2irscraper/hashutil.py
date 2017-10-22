# -*- coding: utf-8 -*-
"""
bmsid/courseid とハッシュ値との相互変換
"""

from lr2irscraper.helper.fetch import *
from lr2irscraper.helper.dataextraction import *
from lr2irscraper.helper.validation import *
from lr2irscraper.helper.exceptions import UnregisteredError


def hash_to_bmsid(hash_value: str) -> int:
    """ BMS のハッシュ値から bmsid を得る。

    Args:
        hash_value: ハッシュ値

    Returns: bmsid

    """
    validate_bms_hash(hash_value)
    try:
        very_large_page_number = 4294967295  # 大きいページ数を指定してランキングの表示件数を 0 件にしている
        return read_bmsid_from_html(fetch_ranking_html(hash_value, mode="hash", page=very_large_page_number))
    except ParseError:
        raise UnregisteredError(hash_value, "hash")


def hash_to_courseid(hash_value: str) -> int:
    """ コースのハッシュ値から courseid を得る。

    Args:
        hash_value: ハッシュ値

    Returns: courseid

    """
    validate_course_hash(hash_value)
    try:
        very_large_page_number = 4294967295  # 大きいページ数を指定してランキングの表示件数を 0 件にしている
        return read_courseid_from_html(fetch_ranking_html(hash_value, mode="hash", page=very_large_page_number))
    except ParseError:
        raise UnregisteredError(hash_value, "hash")


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


def courseid_to_hash(courseid: int) -> str:
    """ courseid からコースのハッシュ値を得る。

    Args:
        courseid: courseid

    Returns: ハッシュ値

    """
    validate_id(courseid)
    try:
        return read_course_hash_from_course_file(fetch_course_file(courseid))
    except ParseError:
        raise UnregisteredError(courseid, "courseid")