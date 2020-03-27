import pytest


from lr2irscraper import Ranking
from .util import resource


@pytest.mark.parametrize("source,shape,value", [
    (resource("ranking/test.xml"), (318, 8), ("nakt", 35564, 5, 501, 501, 417, 80, 0)),
    (resource("ranking/test_course.xml"), (95, 8), ("nakt", 35564, 1, 8156, 404, 2057, 1413, 4434))
])
def test_parse_ranking_xml(source, shape, value):
    df = Ranking(source).to_dataframe()
    assert df.shape == shape
    assert tuple(df.query("id == 35564").values[0]) == value
