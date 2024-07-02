# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

import pytest
from dataclasses import dataclass
from classifiedjson import dumps, loads


@dataclass
class MyConfig:
    max: int = None
    min: int = -100

    def create_affiliate(self):
        return MySubject(self)

class MySubject:
    def __init__(self, config: MyConfig):
        self.config = config
        self.limit = 5 * config.max


@dataclass
class MyConfigMissing:
    avg: int = 99
    mean: int = 78


def test_basic():
    c = MyConfig(max=1000)
    s = c.create_affiliate()
    assert s.config.min == -100
    assert s.config.max == 1000


def test_serialized():
    config = MyConfig(max=2000)
    s = dumps(config)
    config2 = loads(s)
    assert config == config2
    subject2 = config2.create_affiliate()
    assert subject2.limit == 10000


def test_missing():
    config = MyConfigMissing()
    # forgot to add create_affiliate function
    with pytest.raises(AttributeError) as e_info:
        config.create_affiliate()
