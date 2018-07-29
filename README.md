lr2irscraper
===
[LR2IR (LunaticRave2 Internet Ranking)](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi) Scraper Library for Python 3 


## Installation
```
$ pip install git+https://github.com/naktazdim/lr2irscraper
```

## Requirements
* Python 3.5 or later
* [Pandas](https://pandas.pydata.org/) 0.21 or later
* [Requests](http://requests-docs-ja.readthedocs.io/en/latest/)
* [pyjsparser](https://github.com/PiotrDabkowski/pyjsparser)

## Example
```python
import lr2irscraper

# Get LR2IR data (as pandas.DataFrame)
table = lr2irscraper.get_bms_table("http://nekokan.dyndns.info/~lobsak/genocide/insane.html")
ranking = lr2irscraper.get_ranking_data("bbe56a302c1cefd8cd61cbd440354361")
ranking_detail = lr2irscraper.get_ranking_data_detail(234264, "bmsid")

# save as csv
table.to_csv("table.csv", index=False)
ranking.to_csv("ranking.csv", index=False)
ranking_detail.to_csv("ranking_detail.csv", index=False)
```
