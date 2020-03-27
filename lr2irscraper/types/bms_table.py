from typing import Dict, Any
from dataclasses import dataclass
from urllib.parse import urljoin
from io import BytesIO
import json

import lxml.html
import pandas as pd
from pandas import CategoricalDtype

from lr2irscraper.helper.fetch import fetch


def _fetch_bmstable_json(url: str) -> Dict[str, Any]:
    # 仕様で UTF-8 と決まっている。"utf-8" だと BOM あり UTF-8 が読めない。 utf-8-sig は BOM ありもなしもどちらも読める
    return json.loads(fetch(url).decode("utf-8-sig"))


@dataclass()
class BmsTable(object):
    header: dict
    data: dict

    @classmethod
    def from_source(cls, header_source: str, data_source: str) -> "BmsTable":
        return BmsTable(
            json.load(open(header_source)),
            json.load(open(data_source)) if data_source else None
        )

    @classmethod
    def from_url(cls, url: str) -> "BmsTable":
        html = fetch(url)
        tree = lxml.html.parse(BytesIO(html))

        header_json_path = urljoin(url, tree.xpath("/html/head/meta[@name='bmstable']/@content")[0])
        header = _fetch_bmstable_json(header_json_path)
        data_json_path = urljoin(header_json_path, header["data_url"])
        data = _fetch_bmstable_json(data_json_path)
        return BmsTable(header, data)

    def to_dict(self) -> dict:
        return {
            "header": self.header,
            "data": self.data
        }

    def to_dataframe(self) -> pd.DataFrame:
        """次期難易度表フォーマットのデータを DataFrame として返す。

        "level" カラムは Categorical, 他のカラムはすべて文字列 (object 型) とする。
        表記レベルの先頭にはシンボルを付加する (たとえば "▼0")。
        欠損値は空文字列とする。

        :return: DataFrame
        """
        assert self.data is not None

        if len(self.data) == 0:
            # 空の場合も、仕様上の必須カラムは用意しておく。"level" カラムは存在しないと以下の処理で困る
            table = pd.DataFrame(columns=["md5", "level"], dtype=object)
        else:
            table = pd.DataFrame.from_dict(self.data, dtype=object).fillna("")

        tag = self.header.get("tag") or self.header["symbol"]
        level_order = self.header.get("level_order") or table["level"].drop_duplicates().values
        level_order = list(map(str, level_order))  # 仕様では Array(String | Integer) となっている。str に統一しておく。

        return (
            table
                .astype({"level": str})  # 仕様では str なのだが、int が入っていることがある (例: 新 Overjoy) ので str に統一しておく
                .astype({"level": CategoricalDtype(categories=level_order, ordered=True)})
                .assign(level=lambda df: df["level"].cat.rename_categories([tag + level for level in level_order]))
        )
