# -*- coding: utf-8 -*-
import unittest

from lr2irscraper.helper.dataextraction.bmstablenewstyle import *
from tests.util import resource


class TestDataExtractionBMSTable(unittest.TestCase):
    def test_extract_header_path(self):
        files = ["insane.html", "overjoy.html", "second_insane.html"]
        encodings = ["cp932", "utf-8", "cp932"]
        answers = [None, None, "js/insane_header.json"]

        for file, encoding, answer in zip(files, encodings, answers):
            with self.subTest(file=file):
                source = resource(file, encoding)
                self.assertEqual(extract_header_path(source), answer)

    def test_extract_data_path(self):
        source = resource("second_insane_header.json", "utf-8-sig")
        self.assertEqual(extract_data_path(source), "/js/insane_data.json")

    def test_make_dataframe_from_header_and_data_json(self):
        header_files = ["second_insane_header.json",
                        "second_insane_header_without_tag.json",
                        "second_insane_header_without_level_order.json"]

        data = resource("second_insane_data.json", "utf-8-sig")

        level_order = [
            "▼0-", "▼0",
            "▼1", "▼2", "▼3", "▼4", "▼5", "▼6", "▼7", "▼8", "▼9", "▼10",
            "▼11", "▼12", "▼13", "▼14", "▼15", "▼16", "▼17", "▼18", "▼19", "▼20",
            "▼21", "▼22", "▼23", "▼24",
            "▼?"
        ]

        magical_taterenda = \
            ['源屋feat.ユスラ', '隔離枠その2。縦連。▼2はS乱での難易度。削除提案で問題に挙がった曲です。',
             0, 3, '▼?', 93156, '508330b4bc4513536aea7945d90909e2', 'JLS', '',
             '00000000020000000300000003000000030000000400000005000000030001000400000003000000'
             '03000000040000000400000008000100130000001200000011000000150000001100000012000000'
             '13000000120000001100000014000000120000001400000014000000130000001300000014000000'
             '13000000140000001400000013000000130000001500000012000000070000000800010010000000'
             '10000000140000001000000013000000150000001200000011000000140000001000000010000400'
             '13000000110000001200000018000000120001001300000014000000120000001300000015000000'
             '12000000130000001400000013000000130000001400000013000100130000001400000012000000'
             '13000000150000001200000013000000140000001300000013000000200000001400010008000000'
             '07000000080000000800000009000000080000000800000008000000070000000900000011000000'
             '15000000080001001100000012000000130000001100000013000000120000001100000011000000'
             '09000000130000001000000007000000030000000300000007000000030000000300000007000000'
             '03000000020000000300000004000000110000001700000015000100150000001300000017000000'
             '14000000140000001700000014000000130000001700000020000000210000001400010000000000',
             '', '', '', 0, '', 'マジカル縦連打', 450.0,
             'http://manbow.nothing.sh/event/event.cgi?action=More_def&num=86&event=36',
             'http://gooeybms.web.fc2.com/index.html', '']

        for header_file in header_files:
            header = resource(header_file, "utf-8-sig")
            table = make_dataframe_from_header_and_data_json(header, data)
            self.assertListEqual(list(table.level.cat.categories.values), level_order)
            self.assertListEqual(list(table.iloc[839].values), magical_taterenda)


if __name__ == '__main__':
    unittest.main()
