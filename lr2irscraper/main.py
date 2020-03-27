from lr2irscraper import BmsTable, BmsInfo, Ranking
from lr2irscraper.bmsmd5 import BmsMd5


def get_bms_table(url: str) -> BmsTable:
    return BmsTable.from_url(url)


def get_bms_info(bmsmd5: str) -> BmsInfo:
    return BmsInfo.from_bmsmd5(BmsMd5(bmsmd5))


def get_ranking(bmsmd5: str) -> Ranking:
    return Ranking.from_bmsmd5(BmsMd5(bmsmd5))
