# -*- coding: utf-8 -*-
import unittest
import os
import codecs

from lr2irscraper.helper.dataextraction import *


class TestDataExtraction(unittest.TestCase):
    @classmethod
    def resource(cls, name: str, encoding: str="cp932"):
        path = os.path.join(os.path.dirname(__file__), "resources", name)
        with codecs.open(path, "r", encoding) as f:
            return f.read()

    def test_parse_ranking_xml(self):
        files = ["test.xml", "test_course.xml"]
        shapes = [(318, 8), (95, 8)]
        values = [(35564, "nakt", 5, 501, 501, 417, 80, 0), (35564, "nakt", 1, 8156, 404, 2057, 1413, 4434)]

        for file, shape, value in zip(files, shapes, values):
            with self.subTest(file):
                df = extract_ranking_from_xml(self.resource(file))
                self.assertEqual(df.shape, shape)
                self.assertEqual(tuple(df[df["id"] == 35564].values[0]), value)

    def test_extract_ranking_from_html(self):
        df = extract_ranking_from_html(self.resource("test_middle.html"))
        self.assertEqual(
            tuple(df[df["id"] == 35564].values[0]),
            (6645, 35564,  "nakt", "★04", "-", "HARD", "AAA", 3608, 4012, "89.93%",
             1404, 2006, 10, 1628, 352, 20, 3, 9, "易", "乱", "BM", "LR2", ""))

        files = ["test_head.html", "test_middle.html", "test_tail.html", "test_less_than_100.html", "test_course.html"]
        sizes = [100, 100, 53, 25, 100]
        for file, size in zip(files, sizes):
            with self.subTest(file=file):
                df = extract_ranking_from_html(self.resource(file))
                self.assertEqual(df.shape, (size, 23))
                self.assertTrue(df.notnull().values.all())

    def test_extract_ranking_from_html_error(self):
        files = ["test_out_of_bounds.html", "test_unregistered.html", "test_unregistered2.html"]
        for file in files:
            with self.subTest(file=file):
                self.assertRaises(ParseError, extract_ranking_from_html, self.resource(file))

    def test_read_player_count_from_html(self):
        files = ["test_head.html", "test_middle.html", "test_tail.html", "test_less_than_100.html", "test_course.html"]
        player_counts = [22553, 22553, 22553, 25, 11370]

        for file, player_count in zip(files, player_counts):
            with self.subTest(file=file):
                self.assertEqual(read_player_count_from_html(self.resource(file)),
                                 player_count)

    def test_chart_unregistered(self):
        files = ["test_middle.html", "test_less_than_100.html", "test_course.html",
                 "test_unregistered.html", "test_unregistered2.html"]
        answers = [False, False, False, True, True]

        for file, answer in zip(files, answers):
            with self.subTest(file=file):
                self.assertEqual(chart_unregistered(self.resource(file)), answer)

    def test_read_bmsid_from_html(self):
        files = ["test_middle.html", "test_less_than_100.html"]
        bmsids = [15, 4]

        for file, bmsid in zip(files, bmsids):
            with self.subTest(file=file):
                self.assertEqual(read_bmsid_from_html(self.resource(file)), bmsid)

    def test_read_courseid_from_html(self):
        files = ["test_course.html"]
        bmsids = [4945]

        for file, bmsid in zip(files, bmsids):
            with self.subTest(file=file):
                self.assertEqual(read_courseid_from_html(self.resource(file)), bmsid)

    def test_read_course_hash_from_course_file(self):
        files = ["course.lr2crs"]
        course_hashes = ["00000000002000000000000000005190"
                         "c07125de4ed7fbe7cb066cc41e50e51e"
                         "fc7d46e7bbc9f6afd26d05e3bf2ef555"
                         "b3887714270e28988ce900e4b9300994"
                         "d1877ad5dc0134b27eb0238da5721eed"]

        for file, course_hash in zip(files, course_hashes):
            with self.subTest(file=file):
                self.assertEqual(read_course_hash_from_course_file(self.resource(file)), course_hash)

    def test_extract_old_style_bms_table(self):
        insane = extract_bms_table_from_html(self.resource("insane.html"))
        self.assertEqual(tuple(insane.iloc[0]),
                         ("★1", "星の器～STAR OF ANDROMEDA (ANOTHER)", 15,
                          "<a href='http://bit.ly/eoD0dZ'>ZUN (Arr.sun3)</a>",
                          "<a href=''></a>",
                          ""))

        overjoy = extract_bms_table_from_html(self.resource("overjoy.html", "utf-8"), is_overjoy=True)
        self.assertEqual(tuple(overjoy.iloc[201]),
                         ("★★5", "FREEDOM DiVE [FOUR DIMENSIONS]", 1031,
                          "<a href='http://manbow.nothing.sh/event/event.cgi"
                          "?action=More_def&num=15&event=50'>MAXBEAT</a>",
                          "<a href='http://airlab.web.fc2.com/'>air</a>",
                          ""))


if __name__ == '__main__':
    unittest.main()
