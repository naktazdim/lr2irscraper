import pytest

from lr2irscraper import BmsTable
from tests.util import resource_path


@pytest.mark.parametrize("url", [
    resource_path("bms_table/insane/insane.html"),
    resource_path("bms_table/overjoy/overjoy.html"),
    resource_path("bms_table/second_insane/second_insane.html"),
])
def test_bms_table(url):
    # とりあえず読めることを確認
    BmsTable.from_url(resource_path("bms_table/second_insane/second_insane.html")).to_dataframe()
