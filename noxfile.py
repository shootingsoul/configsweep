# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

import nox

@nox.session(
    python=["3.8", "3.9", "3.10", "3.11", "3.12"]
)
def test(session):
    session.install(".")
    session.install("pytest")
    session.install("classifiedjson")

    session.run("pytest", "tests/")