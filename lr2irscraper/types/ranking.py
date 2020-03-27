from dataclasses import dataclass
import re

import pandas as pd

from lr2irscraper.types import BmsMd5
from lr2irscraper.helper.fetch import fetch


@dataclass()
class Ranking:
    """LR2のランキングAPIの出力
    http://www.dream-pro.info/~lavalse/LR2IR/2/getrankingxml.cgi?id=[playerid]&songmd5=[songmd5]
    """
    source: str

    @classmethod
    def from_bmsmd5(cls, bmsmd5: BmsMd5) -> "Ranking":
        """ bmsmd5を指定してランキングを取得する。

        :param bmsmd5: bmsmd5
        :return: Ranking
        """
        return Ranking(fetch("http://www.dream-pro.info/~lavalse/LR2IR"
                       "/2/getrankingxml.cgi?id=1&songmd5={}".format(bmsmd5.hash))
                       .decode("cp932"))

    def to_dataframe(self) -> pd.DataFrame:
        """ランキングをDataFrameの形で返す。

        :return: ランキングデータ
                 (id, name, clear, notes, combo, pg, gr, minbp)
                 clear は 1-5 の数値で、FAILED, EASY, CLEAR, HARD, FULLCOMBO に対応する。
                 ★FULLCOMBO の情報は取得できない (FULLCOMBO と同じく 5 になる)。
        """

        """
        上記APIの出力は以下のような形式をしている。

        #<?xml version="1.0" encoding="shift_jis"?>
        <ranking>
            <score>
                <name>nakt</name>
                <id>35564</id>
                <clear>4</clear>
                <notes>1797</notes>
                <combo>602</combo>
                <pg>1003</pg>
                <gr>680</gr>
                <minbp>39</minbp>
            </score>
            ...
            <score>
                ...
            </score>
        </ranking>
        <lastupdate></lastupdate>

        これはwell-formedなXMLではない (1行目の先頭に # がある、ルート要素が <ranking> と <lastupdate> の2つある)。
        なので、XMLパーサは使わずに単に正規表現でデータを抜き出してしまうほうが楽 (だし速度も速い)。
        """
        columns = ["name", "playerid", "clear", "notes", "combo", "pg", "gr", "minbp"]
        match = re.findall(r"<.*?>(.*?)</.*?>", self.source)[:-1]  # タグの中身をlistで抽出。[:-1]は<lastupdate>の分を抜いている
        data = [match[i:i + len(columns)] for i in range(0, len(match), len(columns))]  # len(columns) 個ずつ区切る
        return pd.DataFrame(data, columns=columns)
