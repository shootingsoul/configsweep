# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import List


@dataclass
class Sweep:
    """
    Replace the value in a config with a Sweep object with a list of values to sweep over

    values - list of values to sweep over
    Priority - priorty relative to other sweep objects.
               Higher priorty items group their values together in the combinations
    """
    values: List = field(default_factory=lambda: [])
    priority: int = 0
