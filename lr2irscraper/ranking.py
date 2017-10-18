# -*- coding: utf-8 -*-
from time import sleep

import pandas as pd

from lr2irscraper.helper.fetch import *
from lr2irscraper.helper.dataextraction import *
from lr2irscraper.helper.validation import *
from lr2irscraper.helper.exceptions import RankingChangedError, UnregisteredError


def get_ranking_data_by_hash(hash_value: str) -> pd.DataFrame:
    """ ハッシュ値からランキングデータを取得する。

    Args:
        hash_value: ハッシュ値 (bms の場合は 32 桁、コースの場合は 160 桁の 16 進数値)

    Returns:
        ランキングデータ
        name, clear, notes, combo, pg, gr, minbp

    """
    validate_hash(hash_value)
    return extract_ranking_from_xml(fetch_ranking_xml(hash_value))


def get_ranking_data_by_id(bmsid: int, mode: str="bms", interval: float=1.0) -> pd.DataFrame:
    """ bmsid を与えるとランキングデータを返す。

    1 ページ (100 件) ずつランキングページを読み取ってデータを取得する。
    get_ranking_data_by_hash() より多くの情報が得られるが、低速。取得中にランキングが更新されてしまい失敗することがある。
    ハッシュ値がわかっていて get_ranking_data_by_hash() のデータで事足りる場合は極力そちらを使用すること。

    Args:
        bmsid: bmsid または courseid
        mode: BMS の場合は "bms"、コースの場合は "course" を指定
        interval: 1ページ取得するごとに interval 秒だけ間隔をあける (サーバに負荷をかけすぎないため)

    Returns:
        ランキングデータ
        rank, name, sp_dan, dp_dan, clear, dj_level, score, max_score, score_percentage,
        combo, notes, minbp, pg, gr, gd, bd, pr, gauge_option, random_option, input, body, comments

    """
    validate_id(bmsid)
    if not (mode in ["bms", "course"]):
        raise ValueError("{}: mode must be 'bms' or 'course'".format(mode))

    # まず 1 ページ目を取得し、そこから諸々の情報を得る
    source = fetch_ranking_html_by_id(bmsid, mode, 1)

    if chart_unregistered(source):
        raise UnregisteredError(bmsid, mode + "id")

    player_count = read_player_count_from_html(source)  # プレイヤ数を取得 (ランキング更新の判定に使う)
    page_count = (player_count + 99) // 100  # プレイヤ数を 100 で割って切り上げるとページ数

    data_frames = [extract_ranking_from_html(source)]  # 以下でここに各ページを DataFrame に変換したものを格納
    player_ids = set(data_frames[0].index)  # プレイヤ ID の集合 (ランキング更新の判定に使う)

    # 2 ページ目以降を順に取得
    for page in range(2, page_count + 1):
        sleep(interval)

        source = fetch_ranking_html_by_id(bmsid, mode, page)

        if read_player_count_from_html(source) != player_count:  # もしプレイヤ数が変化していたら
            raise RankingChangedError  # 途中でランキングが更新されてしまっている

        data_frames.append(extract_ranking_from_html(source))

        index = set(data_frames[-1].index)  # このページのプレイヤ ID の集合
        if player_ids & index:  # に、もし今までに見たプレイヤ ID と 1 つでも重複があれば
            raise RankingChangedError  # 途中でランキングが更新されてしまっている

        player_ids |= index  # プレイヤ ID の集合を更新

    return pd.concat(data_frames)  # 全ページのデータを結合して返す

