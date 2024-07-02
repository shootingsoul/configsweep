# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

from copy import deepcopy
from configsweep.sweep_dag import SweepDag
from configsweep.sweep_combination import SweepCombination
from typing import Any, List, Union


class Sweeper:
    """
    Iterator sweeps over a config with Sweep objects
    Each iteration replaces each sweep object with a combinations of values
    Nested sweep objects are supported
    
    NOTE: a copy of the config is made and copies of the config for each combination are made
    """

    def __init__(self, config: Union[Any, List]):
        if config is None:
            config_list = []
        else:
            config_list = config if isinstance(config, list) else [config]

        # create a copy of the config to hack up and sweep through the Sweep class value list combos
        # if no copy is made:
        #   Config is shared for all combos and put back in place after all sweeps
        #   This means each sweepcombination.config is lost on the next iteration
        #   Exiting the sweeper before completion all combinations will leave config in a bad state
        # So we won't expose this option for now
        self._copy = True
        self._config_templates = [
            deepcopy(s) for s in config_list] if self._copy else config_list
        self._dags = [SweepDag(s) for s in self._config_templates]
        self._len = 0
        for d in self._dags:
            self._len += len(d.root_node.combos)
        self._current_dag = None

    def __len__(self) -> int:
        return self._len

    def __iter__(self):
        self._pos = 0
        self._dag_index = 0
        self._combo_index = 0
        if self._len:
            self._current_dag = self._dags[self._dag_index]
        else:
            self._current_dag = None
        return self

    def __next__(self) -> SweepCombination:
        # beating a dead horse
        if self._current_dag is None:
            raise StopIteration

        # see if we are done with combos for the current dag
        if self._combo_index == len(self._current_dag.root_node.combos):
            if not self._copy:
                # set config back the way it was to start with the sweep objects in place
                # only needed if not copying
                self._current_dag.apply_sweep_to_config()
            # on to the next config/dag if available
            self._dag_index += 1
            self._combo_index = 0  # reset pos to iterate through next dag
            if self._dag_index == len(self._dags):
                self._current_dag = None  # fin
                raise StopIteration
            else:
                self._current_dag = self._dags[self._dag_index]

        # apply the combo to substitute values in the config
        # get a description of the substitutions made
        description_list = self._current_dag.apply_combo_to_config(
            self._combo_index)

        # return a copy of the config with all sweep values replaced
        # also include description of the sweep combination used
        if self._copy:
            config = deepcopy(self._config_templates[self._dag_index])
        else:
            config = self._config_templates[self._dag_index]

        combo = SweepCombination(
            "\n".join(description_list), config, self._pos)
        # prep for next combo
        self._combo_index += 1
        self._pos += 1
        return combo
