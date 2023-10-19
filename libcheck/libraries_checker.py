#!/usr/bin/env python3
"""Libraries checker"""
from libcheck.management.commands.check_libraries import CheckerCommand

class LibrariesChecker:

    checker = None
    def __init__(self):
        self.checker = CheckerCommand()

    def check(self):
        self.checker.check()
        return
