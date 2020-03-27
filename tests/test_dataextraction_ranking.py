import unittest

from lr2irscraper.helper.data_extraction.ranking import *
from tests.util import resource


class TestDataExtractionRanking(unittest.TestCase):
    def test_parse_ranking_xml(self):
        files = ["test.xml", "test_course.xml"]
        shapes = [(318, 8), (95, 8)]
        values = [(35564, "nakt", 5, 501, 501, 417, 80, 0), (35564, "nakt", 1, 8156, 404, 2057, 1413, 4434)]

        for file, shape, value in zip(files, shapes, values):
            with self.subTest(file):
                df = extract_ranking_from_xml(resource(file))
                self.assertEqual(df.shape, shape)
                self.assertEqual(tuple(df[df["id"] == 35564].values[0]), value)

    def test_read_player_count_from_html(self):
        files = ["test_head.html", "test_middle.html", "test_tail.html", "test_less_than_100.html", "test_course.html"]
        player_counts = [22553, 22553, 22553, 25, 11370]

        for file, player_count in zip(files, player_counts):
            with self.subTest(file=file):
                self.assertEqual(read_player_count_from_html(resource(file)),
                                 player_count)

    def test_chart_unregistered(self):
        files = ["test_middle.html", "test_less_than_100.html", "test_course.html",
                 "test_unregistered.html", "test_unregistered2.html"]
        answers = [False, False, False, True, True]

        for file, answer in zip(files, answers):
            with self.subTest(file=file):
                self.assertEqual(chart_unregistered(resource(file)), answer)

    def test_read_bmsid_from_html(self):
        files = ["test_middle.html", "test_less_than_100.html"]
        bmsids = [15, 4]

        for file, bmsid in zip(files, bmsids):
            with self.subTest(file=file):
                self.assertEqual(read_bmsid_from_html(resource(file)), bmsid)

    def test_read_courseid_from_html(self):
        files = ["test_course.html"]
        bmsids = [4945]

        for file, bmsid in zip(files, bmsids):
            with self.subTest(file=file):
                self.assertEqual(read_courseid_from_html(resource(file)), bmsid)

    def test_read_course_hash_from_course_file(self):
        files = ["course.lr2crs"]
        course_hashes = ["00000000002000000000000000005190"
                         "c07125de4ed7fbe7cb066cc41e50e51e"
                         "fc7d46e7bbc9f6afd26d05e3bf2ef555"
                         "b3887714270e28988ce900e4b9300994"
                         "d1877ad5dc0134b27eb0238da5721eed"]

        for file, course_hash in zip(files, course_hashes):
            with self.subTest(file=file):
                self.assertEqual(read_course_hash_from_course_file(resource(file)), course_hash)


if __name__ == '__main__':
    unittest.main()
