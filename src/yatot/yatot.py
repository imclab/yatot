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
import matplotlib.pyplot as plt

class Yatot:


    def __init__(self, db):
        self._db = db
        self._cli = cli.CLI(self)
        self._hints = []
        self._graph = nx.MultiDiGraph()


    def play(self):
        self._cli.cmdloop()


    def getHints(self):
        return self._hints


    def _hintGiven(self, hint):
        self._hints.append(hint)
        hintID = self._db.queryNodeIDByName(hint)
        if len(hintID) == 0:
            self._cli.printMsg("Unknown word : {0}".format(hint))
            return
        if len(hintID) > 1:
            log.warning("There are more than one node with name: %s. " \
                        "Picking the first one", hint)
        hintID = hintID[0]["nID"]
        hintDatas = self._db.queryNodeByID(hintID)
        neighbourhood = self._db.queryNodeNeighbourhoodByID(hintID)
        self._addNode(hintDatas)
        self._addNeighbourhood(hintID, neighbourhood)
        # self._drawGraph()


    def _addNode(self, node):
        self._graph.add_node(node["nID"],             \
                             nName   = node["nName"], \
                             nType   = node["nType"], \
                             nWeight = node["nWeight"])


    def _addNeighbourhood(self, nID, neighbourhood):
        for entry in neighbourhood:
            self._graph.add_node(entry["rOther"],            \
                                 nName   = entry["N.nName"], \
                                 nType   = entry["N.nType"], \
                                 nWeight = entry["N.nWeight"])
            self._graph.add_edge(nID, entry["rOther"],       \
                                 rID     = entry["R.rID"],   \
                                 rType   = entry["R.rType"], \
                                 rWeight = entry["R.rWeight"])


    def _drawGraph(self):
        # lbls = {}
        # for node in self._graph.nodes():
        #     lbls[node] = self._graph.node[node]
        nx.draw_networkx(self._graph)
        plt.savefig("{0}.png".format(len(self._hints)))
