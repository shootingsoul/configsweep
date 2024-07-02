# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

from configsweep.affiliate import ICreateAffiliate
from configsweep.sweep import Sweep
from configsweep.sweep_combination import SweepCombination
from configsweep.sweeper import Sweeper

__version__ = "1.0.0"
__all__ = (__version__,
           ICreateAffiliate,
           Sweep,
           Sweeper,
           SweepCombination)
