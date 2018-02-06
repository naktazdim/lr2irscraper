# -*- coding: utf-8 -*-

import argparse
import re
import os
import traceback
from typing import Tuple, Union
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import pandas as pd
import numpy as np

from lr2irscraper import get_bms_table

from tests.util import resource_path


lock = Lock()


def try_get_bms_table(args: Tuple[str, str, str]) -> bool:
    name, url, output_directory = args
    name = re.sub(r'[\\/:*?"<>|]', "_", name)

    try:
        bms_table = get_bms_table(url)
        bms_table.to_csv(os.path.join(output_directory, "{}.csv".format(name)), index=False)
        with lock:
            print("OK: [{} ({})]".format(name, url), flush=True)
        return True
    except Exception:
        with lock:
            print("Failed: [{} ({})]".format(name, url), flush=True)
        with open(os.path.join(output_directory, "traceback_{}.txt".format(name)), "w") as f:
            f.write(traceback.format_exc())
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output_directory")
    args = p.parse_args()

    tpe = ThreadPoolExecutor(max_workers=100)
    bms_table_table = pd.read_csv(resource_path("bms_tables.csv"))

    print("test get_bms_table() for {} tables ...".format(len(bms_table_table)))
    results = list(tpe.map(try_get_bms_table,
                           [(name, url, args.output_directory)
                            for _, (name, url) in bms_table_table.iterrows()]))

    print("{} / {} failed".format(len(results) - np.count_nonzero(results), len(results)))


if __name__ == "__main__":
    main()
