import os
import codecs


def resource_path(name: str):
    return os.path.join(os.path.dirname(__file__), "resources", name)


def resource(name: str, encoding: str = "cp932"):
    with codecs.open(resource_path(name), "r", encoding) as f:
        return f.read()
