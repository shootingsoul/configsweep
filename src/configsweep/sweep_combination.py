# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

from typing import Any


class SweepCombination:
    """
    A config with values set for a combination of sweep items defined in the original config

    description - what values where set for this combination
    config - the config with all sweep items replaced with values
    index - a unique index across all the sweep combinations
    """

    def __init__(self, description: str, config: Any, index: int):
        # description of the sweep values used in this combination
        self.description = description
        self.config = config
        self.index = index

    def __repr__(self) -> str:
        return f"SweepCombination(index={self.index} description={self.description}, config={self.config})"
