# -*- coding: utf-8 -*-
import re


def validate_id(bmsid: int):
    if int(bmsid) <= 0:
        raise ValueError("{}: id must be a positive integer".format(bmsid))


def validate_hash(hash_value: str):
    if not re.match("^([0-9a-f]{32}|[0-9a-f]{160})$", hash_value):
        raise ValueError("{}: hash must be 32 or 160 hexadecimal digits".format(hash))


def validate_bms_hash(hash_value: str):
    if not re.match("^[0-9a-f]{32}$", hash_value):
        raise ValueError("{}: BMS hash must be 32 hexadecimal digits".format(hash))


def validate_course_hash(hash_value: str):
    if not re.match("^[0-9a-f]{160}$", hash_value):
        raise ValueError("{}: course hash must be 160 hexadecimal digits".format(hash))
