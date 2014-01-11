#!/usr/bin/python
# -*- coding: utf-8 -*-

# ############################################################################
# yatot.py
# Authors:
#   * -kc- <kevin.cousot at gmail.com>
#   * Rider Carrion <rider.carrion at gmail.com>
# Description: 
# ============================================================================
# Notes:
#
# ############################################################################

import cli
import logging as log
import networkx as nx

class Yatot:
    
    def __init__(self, db):
        self._db = db
        self._cli = cli.CLI(self)

    def play(self):
        self._cli.cmdloop()
