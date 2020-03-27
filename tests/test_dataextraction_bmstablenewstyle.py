import unittest

from lr2irscraper.helper.data_extraction.bms_table_new_style import *
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

        for header_file in header_files:
            header = resource(header_file, "utf-8-sig")
            table = make_dataframe_from_header_and_data_json(header, data)
            self.assertListEqual(list(table.level.cat.categories.values), level_order)
            self.assertListEqual(list(table.loc[839, ["level", "md5", "lr2_bmsid", "title"]]),
                                 ["▼?", "508330b4bc4513536aea7945d90909e2", 93156, "マジカル縦連打"])


if __name__ == '__main__':
    unittest.main()
