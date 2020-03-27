lr2irscraper
===
Simple [LR2IR (LunaticRave2 Internet Ranking)](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi) Scraping Library for Python


## Installation
```
$ pip install git+https://github.com/naktazdim/lr2irscraper
```

## Requirements
* Python 3.7 or later
* [Pandas](https://pandas.pydata.org/) 0.21 or later
* [Requests](http://requests-docs-ja.readthedocs.io/en/latest/)
* [lxml](https://lxml.de/)

## Examples
```python
import lr2irscraper

# BMS Table
table = lr2irscraper.get_bms_table("http://www.ribbit.xyz/bms/tables/insane.html")
table_dict = table.to_dict()  # as dict
table_df = table.to_dataframe()  # or as DataFrame

# Ranking
ranking = lr2irscraper.get_ranking("bbe56a302c1cefd8cd61cbd440354361")
ranking_df = ranking.to_dataframe()  # as DataFrame

# BMS Info
bms_info = lr2irscraper.get_bms_info("f8dcdfe070630bbb365323c662561a1a")
# BmsInfo(type='bms', lr2_id=15, title='星の器～STAR OF ANDROMEDA (ANOTHER)')
```
