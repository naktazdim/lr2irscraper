# -*- coding: utf-8 -*-
import os
import codecs


def resource(name: str, encoding: str = "cp932"):
    path = os.path.join(os.path.dirname(__file__), "resources", name)
    with codecs.open(path, "r", encoding) as f:
        return f.read()
