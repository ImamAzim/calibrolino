#!/usr/bin/env python


"""
test all the tools in...
"""

import os
import unittest


from calibrolino import CalibreDBReader


class TestCalibreDBReader(unittest.TestCase):

    """all test concerning CalibreDBReader. """

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        CalibreDBReader()


""" script tests """


if __name__ == '__main__':
    pass
