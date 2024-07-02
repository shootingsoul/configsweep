# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

import pytest
from dataclasses import dataclass, field
from configsweep import Sweep, Sweeper
from enum import Enum
from typing import Any
from copy import deepcopy


class MyDayPart(Enum):
    DAWN = 1
    MORNING = 2
    NOON = 3
    AFTERNOON = 4
    DUSK = 5
    NIGHT = 6


@dataclass
class MyMetric:
    min: int = 0
    max: int = 0


@dataclass
class MySillyMetric:
    target: int = 0
    metric: MyMetric = field(default_factory=lambda: MyMetric())


@dataclass
class MyConfig:
    name: str = ""
    day_part: MyDayPart = MyDayPart.AFTERNOON
    top_three: list[str] = field(default_factory=lambda: [
                                 "Miami", "Chicago", "NY"])
    data: dict = field(default_factory=lambda: {})
    metric: Any = None
    metric_grid: Any = None


def test_no_sweep():
    config = MyConfig("racing")
    sweeper = Sweeper(config)
    assert len(sweeper) == 1
    iterator = iter(sweeper)
    combo = next(sweeper)
    assert combo.config.name == "racing"
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_enum():
    config = MyConfig("racing")
    config.day_part = Sweep([MyDayPart.DAWN, None, MyDayPart.DUSK])
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DAWN
    combo = next(iterator)
    assert combo.config.day_part is None
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DUSK
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_list():
    config = MyConfig("racing", top_three=Sweep(
        [["LA", "NY", "Philly"], ["Maui", "Kauai", "Oahu"], ["1", "2", "3", "4"]]))
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.top_three == ["LA", "NY", "Philly"]
    combo = next(iterator)
    assert combo.config.top_three == ["Maui", "Kauai", "Oahu"]
    combo = next(iterator)
    assert combo.config.top_three == ["1", "2", "3", "4"]
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_list_index():
    config = MyConfig("racing", top_three=["LA", Sweep(
        ["Detroit", "Chicago", None, "NY"]), "Philly"])
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.top_three == ["LA", "Detroit", "Philly"]
    combo = next(iterator)
    assert combo.config.top_three == ["LA", "Chicago", "Philly"]
    combo = next(iterator)
    assert combo.config.top_three == ["LA", None, "Philly"]
    combo = next(iterator)
    assert combo.config.top_three == ["LA", "NY", "Philly"]
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_dict():
    config = MyConfig("racing", data=Sweep(
        [{"hey": 1, "now": 3}, {"hey": 4, "now": 5}]))
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.data == {"hey": 1, "now": 3}
    combo = next(iterator)
    assert combo.config.data == {"hey": 4, "now": 5}
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_dict_attribute():
    config = MyConfig("racing", data={"hey": 1, "now": Sweep([3, 6, 7, 8])})
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.data == {"hey": 1, "now": 3}
    combo = next(iterator)
    assert combo.config.data == {"hey": 1, "now": 6}
    combo = next(iterator)
    assert combo.config.data == {"hey": 1, "now": 7}
    combo = next(iterator)
    assert combo.config.data == {"hey": 1, "now": 8}
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_multiple():
    config = MyConfig("racing", top_three=Sweep(
        [["LA", "NY", "Philly"], ["Maui", "Kauai", "Oahu"], ["1", "2", "3", "4"]]))
    config.day_part = Sweep([MyDayPart.DAWN, MyDayPart.DUSK])
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DAWN
    assert combo.config.top_three == ["LA", "NY", "Philly"]
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DAWN
    assert combo.config.top_three == ["Maui", "Kauai", "Oahu"]
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DAWN
    assert combo.config.top_three == ["1", "2", "3", "4"]
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DUSK
    assert combo.config.top_three == ["LA", "NY", "Philly"]
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DUSK
    assert combo.config.top_three == ["Maui", "Kauai", "Oahu"]
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DUSK
    assert combo.config.top_three == ["1", "2", "3", "4"]
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_class():
    config = MyConfig("racing", metric=Sweep(
        [MyMetric(5, 10), MyMetric(100, 200)]))
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.metric == MyMetric(5, 10)
    combo = next(iterator)
    assert combo.config.metric == MyMetric(100, 200)
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_class_attribute():
    config = MyConfig("racing", metric=MyMetric(max=5))
    config.metric.min = Sweep([0, 1, 2, 3])
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.metric.min == 0
    combo = next(iterator)
    assert combo.config.metric.min == 1
    combo = next(iterator)
    assert combo.config.metric.min == 2
    combo = next(iterator)
    assert combo.config.metric.min == 3
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_value_not_list():
    config = MyConfig("racing", metric=Sweep(123))
    with pytest.raises(ValueError) as e_info:
        Sweeper(config)


def test_one():
    config = MyConfig("racing", metric=Sweep([MyMetric(5, 10)]))
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.metric == MyMetric(5, 10)
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_none():
    config = MyConfig("racing", metric=Sweep(None))
    with pytest.raises(ValueError) as e_info:
        Sweeper(config)


def test_metric_grid():
    config = MyConfig("racing", metric_grid=[[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    config.metric_grid[1][1] = Sweep([1000, 2000])
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config.metric_grid[2][2] == 9
    assert combo.config.metric_grid[1][1] == 1000
    combo = next(iterator)
    assert combo.config.metric_grid[2][2] == 9
    assert combo.config.metric_grid[1][1] == 2000
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_empty_list():
    config = MyConfig("racing", metric=Sweep([]))
    with pytest.raises(ValueError) as e_info:
        Sweeper(config)


def test_sweep_through_tuple():

    # can't swap in a set or tuple, but can further down the chain
    # make sure we traverse set / tuple
    # set/tuple can't be built with sweep, so should be good
    config = {"a": tuple([{"x": 123}, {"y": Sweep([10, 20, 30])}, "c"])}
    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config['a'][1]['y'] == 10
    combo = next(iterator)
    assert combo.config['a'][1]['y'] == 20
    combo = next(iterator)
    assert combo.config['a'][1]['y'] == 30
    with pytest.raises(StopIteration) as e_info:
        next(iterator)


def test_sweep_sweep():
    # test direct nested - not allowed for ambiguity
    # could want to sweep an element in the array or just have a flat array

    # for example
    # config = {"interval": "15", "strategy": {"name": "s1", "max": Sweep([Sweep([10000,90000]),10])}}
    # could want this:
    # config = {"interval": "15", "strategy": {"name": "s1", "max": Sweep([[Sweep([10000,90000]),10]])}}
    # - or could want this-
    # config = {"interval": "15", "strategy": {"name": "s1", "max": Sweep([10000,90000,10])}}

    config = {"interval": "15", "strategy": {
        "name": "s1", "max": Sweep([Sweep([10000, 90000]), 10])}}
    with pytest.raises(TypeError) as e_info:
        sweeper = Sweeper(config)

# copy option not available . . .
# def test_copy():
#     config = {"x": 123, "y": Sweep([10,20,30]), "c": 456 }
#     original_config = deepcopy(config)

#     # first time, let sweeper make a copy and verify config still matches original
#     sweeper = Sweeper(config)
#     iterator = iter(sweeper)
#     combo = next(iterator)
#     assert combo.config['y'] == 10
#     combo = next(iterator)
#     assert combo.config['y'] == 20
#     combo = next(iterator)
#     assert combo.config['y'] == 30
#     with pytest.raises(StopIteration) as e_info:
#         next(iterator)
#     assert config == original_config

#     # second time, no copy, make sure sweep still works
#     # and config matches original after done sweeping
#     # config won't match original while sweeping
#     sweeper = Sweeper(config, copy = False)
#     sweeper._copy
#     iterator = iter(sweeper)
#     combo = next(iterator)
#     assert combo.config['y'] == 10
#     combo = next(iterator)
#     assert combo.config['y'] == 20
#     combo = next(iterator)
#     assert combo.config['y'] == 30
#     with pytest.raises(StopIteration) as e_info:
#         next(iterator)
#     assert config == original_config


def test_multiple_configs():
    config = {"x": 123, "y": Sweep([10, 20, 30]), "c": 456}
    original_config = deepcopy(config)

    config_racing = MyConfig("racing")
    config_racing.day_part = Sweep([MyDayPart.DAWN, None, MyDayPart.DUSK])
    original_config_racing = deepcopy(config_racing)

    sweeper = Sweeper([config, config_racing])
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.config['y'] == 10
    combo = next(iterator)
    assert combo.config['y'] == 20
    combo = next(iterator)
    assert combo.config['y'] == 30

    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DAWN
    combo = next(iterator)
    assert combo.config.day_part is None
    combo = next(iterator)
    assert combo.config.day_part == MyDayPart.DUSK
    with pytest.raises(StopIteration) as e_info:
        next(iterator)

    assert config == original_config
    assert config_racing == original_config_racing

def test_nested_priority():
    config = { "strategy": Sweep([
               {"name": "strategy_one", "max": 10000},
               {"name": "strategy_two", "min": Sweep([10,20,30]), "max": Sweep([10000,90000])}
               ]),
            "datasources": Sweep(["en", "es", "de", "fr"], priority=1)
        }

    sweeper = Sweeper(config)
    iterator = iter(sweeper)
    combo = next(iterator)
    assert combo.description == "datasources=en\nstrategy=<complex_value>[0]"
    combo = next(iterator)
    assert combo.description == "datasources=en\nstrategy=<complex_value>[1] & strategy.min=10\nstrategy=<complex_value>[1] & strategy.max=10000"
