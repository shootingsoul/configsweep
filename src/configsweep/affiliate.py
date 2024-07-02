# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT


from typing import Protocol, TypeVar

T = TypeVar('T')

class ICreateAffiliate(Protocol[T]):
    """
    A config class implements this protocol to support creating the class it configures, i.e. it's affiliate
    """

    def create_affiliate(self) -> T:
        pass