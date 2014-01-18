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
        if hint in self._hints:
            self._cli.printMsg("Already given hint: {0}".format(hint))
            return
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
        self._addNode(hintDatas["nID"], hintDatas["nName"], \
                      hintDatas["nType"], hintDatas["nWeight"])
        self._addNeighbourhood(hintID, neighbourhood)


    def _nodeExists(self, nodeID):
        return self._graph.node.has_key(nodeID)


    def _addNode(self, nodeID, nodeName, nodeType, nodeWeight):
        if not self._nodeExists(nodeID):
            log.info("Adding node : (%s, %s, %s, %s)", \
                     nodeID, nodeName, nodeType, nodeWeight)
            self._graph.add_node(nodeID,             \
                                 nName   = nodeName, \
                                 nType   = nodeType, \
                                 nWeight = nodeWeight)
        else:
            log.warning("Already existing node: %s, %s, %s %s", \
                        nodeID, nodeName, nodeType, nodeWeight)


    def _edgeExists(self, edgeID):
        return self._graph.edge.has_key(edgeID)


    def _addEdge(self, rFrom, rTo, rID, rType, rWeight):
        if not self._edgeExists(rID):
            log.info("Adding edge : (%s, %s, %s, %s, %s)", \
                     rFrom, rTo, rID, rType, rWeight)
            self._graph.add_edge(rFrom, rTo,      \
                                 rID     = rID,   \
                                 rType   = rType, \
                                 rWeight = rWeight)
        else:
            log.warning("Already existing edge: %s, %s, %s", \
                        rID, rType, rWeight)


    def _addNeighbourhood(self, nID, neighbourhood):
        for entry in neighbourhood:
            self._addNode(entry["rOther"],  entry["N.nName"], \
                          entry["N.nType"], entry["N.nWeight"])
            self._addEdge(nID, entry["rOther"], entry["R.rID"], \
                          entry["R.rType"], entry["R.rWeight"])


    def drawGraph(self):
        lbls = {}
        for node in self._graph.nodes():
            lbls[node] = self._graph.node[node]["nName"]
        nx.draw_graphviz(self._graph, prog = "twopi", \
                         with_labels = True, labels = lbls)
        path = "{0}.png".format(len(self._hints))
        plt.savefig(path)
        return path



