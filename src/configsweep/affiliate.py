# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

from typing import ClassVar, Type


class AffiliateClass:
    """
    Mixin for use with a config dataclass.

    This associates the class being configured with the config for easy creation
    """

    _affiliate_cls: ClassVar[Type] = None

    def __init__():
        pass

    def create_affiliate(self, *args, **kwargs):
        """
        Create an instance of the affiliate class for the config.

        This config class is passed as the first argument to the affiliate contstructor
        along with any additional args, kwargs
        """
        if self._affiliate_cls is None:
            raise ValueError(
                f"Affiliate class not set.  Missing the assignment {type(self).__name__}._affiliate_cls = <type>")
        return self._affiliate_cls(self, *args, **kwargs)
