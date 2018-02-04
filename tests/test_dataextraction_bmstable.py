# -*- coding: utf-8 -*-
import unittest

from lr2irscraper.helper.data_extraction.bms_table import *
from tests.util import resource


class TestDataExtractionBMSTable(unittest.TestCase):
    insane_url = "https://nekokan.dyndns.info/~lobsak/genocide/insane.html"
    overjoy_url = "http://achusi.main.jp/overjoy/nanido-luna.php"

    def test_extract_old_style_bms_table(self):
        insane = extract_mname(resource("insane.html"))
        self.assertEqual(tuple(insane.iloc[0]),
                         (1, "★1", "星の器～STAR OF ANDROMEDA (ANOTHER)", "15",
                          "<a href='http://bit.ly/eoD0dZ'>ZUN (Arr.sun3)</a>",
                          "<a href=''></a>",
                          ""))

        overjoy = extract_mname(resource("overjoy.html", encoding="utf-8"))
        self.assertEqual(tuple(overjoy.iloc[201]),
                         (89, "<font color='red'>★5</font>", "FREEDOM DiVE [FOUR DIMENSIONS]",
                          "http://www.dream-pro.info/~lavalse/cgi-bin/scoreview.cgi"
                          "?hash=78e7a4107265c42ef329c2c4f0eedd76",
                          "http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&bmsid=1031",
                          "<a href='http://manbow.nothing.sh/event/event.cgi"
                          "?action=More_def&num=15&event=50'>MAXBEAT</a>",
                          "<a href='http://airlab.web.fc2.com/'>air</a>",
                          ""))


if __name__ == '__main__':
    unittest.main()
