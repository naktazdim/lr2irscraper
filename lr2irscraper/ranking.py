# -*- coding: utf-8 -*-
from time import sleep

from lr2irscraper.helper.fetch import *
from lr2irscraper.helper.data_extraction.ranking import *
from lr2irscraper.helper.validation import *
from lr2irscraper.helper.exceptions import InconsistentDataError, UnregisteredError


def get_ranking_data(hash_value: str) -> pd.DataFrame:
    """ ランキングデータを取得する。ハッシュ値を渡す必要がある。

    Args:
        hash_value: ハッシュ値 (bms の場合は 32 桁、コースの場合は 160 桁の 16 進数値)

    Returns:
        ランキングデータ
        (id, name, clear, notes, combo, pg, gr, minbp)
        clear は 1-5 の数値で、FAILED, EASY, CLEAR, HARD, FULLCOMBO に対応する。
        ★FULLCOMBO の情報は取得できない (FULLCOMBO と同じく 5 になる)。

    """
    validate_hash(hash_value)
    return extract_ranking_from_xml(fetch_ranking_xml(hash_value))


def get_ranking_data_detail(id_or_hash: Union[int, str], mode: str, interval: float=1.0) -> pd.DataFrame:
    """ 詳細なランキングデータを取得する。bmsid (courseid) およびハッシュ値のいずれを渡してもよい。

    1 ページ (100 件) ずつランキングページを読み取ってデータを取得する。
    get_ranking_data() より多くの情報が得られるが、低速。取得中にランキングが更新されてしまい失敗することがある。
    ハッシュ値がわかっていて get_ranking_data() のデータで事足りる場合は極力そちらを使用すること。

    Args:
        id_or_hash: bmsid, courseid またはハッシュ値
        mode: "bmsid", "courseid", "hash" のいずれかを指定
        interval: 1ページ取得するごとに interval 秒だけ間隔をあける (サーバに負荷をかけすぎないため)

    Returns:
        ランキングデータ
        (id, rank, name, sp_dan, dp_dan, clear, dj_level, score, max_score, score_percentage,
         combo, notes, minbp, pg, gr, gd, bd, pr, gauge_option, random_option, input, body, comment)

    """
    if mode in ["bmsid", "courseid"]:
        validate_id(id_or_hash)
    elif mode == "hash":
        validate_hash(id_or_hash)
    else:
        raise ValueError("{}: mode must be 'bmsid', 'courseid' or 'hash'".format(mode))

    # まず 1 ページ目を取得し、そこから諸々の情報を得る
    source = fetch_ranking_html(id_or_hash, mode, 1)

    if chart_unregistered(source):
        raise UnregisteredError(id_or_hash, mode)

    player_count = read_player_count_from_html(source)  # プレイヤ数を取得 (ランキング更新の判定に使う)
    page_count = (player_count + 99) // 100  # プレイヤ数を 100 で割って切り上げるとページ数

    data_frames = [extract_ranking_from_html(source)]  # 以下でここに各ページを DataFrame に変換したものを格納
    player_ids = set(data_frames[0]["id"])  # プレイヤ ID の集合 (ランキング更新の判定に使う)

    # 2 ページ目以降を順に取得
    for page in range(2, page_count + 1):
        sleep(interval)

        source = fetch_ranking_html(id_or_hash, mode, page)

        if read_player_count_from_html(source) != player_count:  # もしプレイヤ数が変化していたら
            raise InconsistentDataError  # 途中でランキングが更新されてしまっているので終了

        data_frames.append(extract_ranking_from_html(source))

        index = set(data_frames[-1]["id"])  # このページのプレイヤ ID の集合
        if player_ids & index:  # に、もし今までに見たプレイヤ ID と 1 つでも重複があれば
            raise InconsistentDataError  # 途中でランキングが更新されてしまっているので終了

        player_ids |= index  # プレイヤ ID の集合を更新

    return pd.concat(data_frames)  # 全ページのデータを結合して返す

