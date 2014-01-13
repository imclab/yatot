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
        self._hints = []


    def play(self):
        self._cli.cmdloop()


    def _hintGiven(self, hint):
        self._hints.append(hint)
        nodeID = self._db.queryNodeIDByName(hint)
        if len(nodeID) == 0:
            self._cli.printMsg("Unknown word : {0}".format(hint))
            return
        if len(nodeID) > 1:
            log.warning("There are more than one node with name: %s. " \
                        "Picking the first one : %s",
                        hint, nodeID[0][0])
        nodeID = nodeID[0][0]
        nodeDatas = self._db.queryNodeDatas(nodeID)
        self._cli.printRow(nodeDatas)
        neighboursIDs = self._db.queryNeighboursByID(nodeID)
        neighboursDatas = {}
        for elt in neighboursIDs:
            neighbourID = elt["neighbour"]
            neighboursDatas[neighbourID] = self._db.queryNodeDatas(neighbourID)
        print neighboursDatas

