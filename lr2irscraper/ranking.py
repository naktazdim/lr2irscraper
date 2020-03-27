from lr2irscraper.helper.fetch import *
from lr2irscraper.helper.data_extraction.ranking import *
from lr2irscraper.types.bmsmd5 import BmsMd5


def get_ranking_data(hash_value: str) -> pd.DataFrame:
    """ランキングデータを取得する。ハッシュ値を渡す必要がある。

    :param hash_value: ハッシュ値 (bms の場合は 32 桁、コースの場合は 160 桁の 16 進数値)
    :return: ランキングデータ
             (id, name, clear, notes, combo, pg, gr, minbp)
             clear は 1-5 の数値で、FAILED, EASY, CLEAR, HARD, FULLCOMBO に対応する。
             ★FULLCOMBO の情報は取得できない (FULLCOMBO と同じく 5 になる)。
    """
    return extract_ranking_from_xml(fetch_ranking_xml(BmsMd5(hash_value)))
