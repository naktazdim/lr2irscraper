import pytest

from lr2irscraper import BmsInfo
from tests.util import resource


@pytest.mark.parametrize("source,bms_info", [
    (resource("bms_info/test.html"), BmsInfo(type="bms", lr2_id=15, title="星の器～STAR OF ANDROMEDA (ANOTHER)")),
    (resource("bms_info/test_course.html"), BmsInfo(type="course", lr2_id=11099, title="GENOSIDE 2018 段位認定 Overjoy")),
])
def test_bms_info(source, bms_info):
    # とりあえず読めることを確認
    assert BmsInfo.from_source(source) == bms_info


def test_to_dict():
    bms_info = BmsInfo(type="bms", lr2_id=15, title="星の器～STAR OF ANDROMEDA (ANOTHER)")
    bms_info_dict = {"type": "bms", "lr2_id": 15, "title": "星の器～STAR OF ANDROMEDA (ANOTHER)"}

    assert bms_info.to_dict() == bms_info_dict


def bms_info_unregistered():
    bms_info = BmsInfo.from_source(resource("bms_info/test_unregistered.html"))
    assert bms_info is None
