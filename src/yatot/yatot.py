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
from networkx.algorithms.simple_paths import all_simple_paths
import matplotlib.pyplot as plt

L = 3

class Yatot:


    def __init__(self, db):
        self._db = db
        self._cli = cli.CLI(self)
        self._hints = []
        self._graph = nx.MultiGraph()
        self._paths = {}
        self._answers = []


    def play(self):
        self._cli.cmdloop()


    def getHints(self):
        return self._hints


    def getGraphInfos(self):
        return nx.info(self._graph)


    def _computeAnswer(self):
        answer = None
        if len(self._hints) == 1:
            answer = self._getStrongestNeighbour(self._hints[0])
        else:
            self._updatePaths()
            nodes = self._nodesToProcess()
            centrality = {}
            for node in nodes:
                centrality[node] = self._computeCentrality(node)
            answer = None
            maxCentrality = 0
            for k, v in centrality.iteritems():
                if v > maxCentrality:
                    answer = k
                    maxCentrality = v
        return answer


    # What if there are several strongest neighbours ?
    def _getStrongestNeighbour(self, node):
        strongestNeighbour = None
        maxWeight = 0
        for neighbour in self._graph[node]:
            edges = self._graph[node][neighbour]
            for edge, attrs in edges.iteritems():
                if abs(attrs["rWeight"]) > maxWeight:
                    strongestNeighbour = neighbour
                    maxWeight = abs(attrs["rWeight"])
        return strongestNeighbour


    def _nodesToProcess(self):
        nodes = self._graph.nodes()
        for hint in self._hints:
            nodes.remove(hint)
        for answer in self._answers:
            nodes.remove(answer)
        return nodes


    def _computeCentrality(self, node):
        centrality = 0
        for i in xrange(len(self._hints)):
            s = self._hints[i]
            for j in xrange(i + 1, len(self._hints)):
                t = self._hints[j]
                d = self._nbOfPaths(s, t)
                if d == 0:
                    continue
                n = self._nbOfPaths(s, t, node)
                centrality = centrality + (n / float(d))
        return centrality


    def _nbOfPaths(self, s, t, v = None):
        nbOfPaths = 0
        paths = self._paths[(s, t)]
        if v is None:
            nbOfPaths = len(paths)
        else:
            for path in paths:
                if v in path:
                    nbOfPaths = nbOfPaths + 1
        return nbOfPaths


    def _hintGiven(self, hint):
        if hint in self._hints:
            self._cli.printMsg("Already given hint: {0}".format(hint))
            return
        hintID = self._getHintID(hint)
        if hintID is None:
            self._cli.printMsg("Unknown word : {0}".format(hint))
            return
        self._hints.append(hintID)
        self._updateGraph(hintID)
        answer = self._computeAnswer()
        self._answers.append(answer)
        self._cli.printMsg(self._graph.node[answer]["nName"])


    def _getHintID(self, hint):
        results = self._db.queryNodeIDByName(hint)
        if len(results) == 0:
            return None
        if len(results) > 1:
            log.warning("There are more than one node with name: %s. " \
                        "Picking the first one", hint)
        return results[0]["nID"]


    def _updateGraph(self, hintID):
        hintDatas = self._db.queryNodeByID(hintID)
        self._addNode(hintDatas["nID"], hintDatas["nName"], \
                      hintDatas["nType"], hintDatas["nWeight"])
        neighbourhood = self._db.queryNodeNeighbourhoodByID(hintID)
        self._addNeighbourhood(hintID, neighbourhood)        


    def _addNode(self, nodeID, nodeName, nodeType, nodeWeight):
        if not self._graph.has_node(nodeID):
            log.debug("Adding node : (%s, %s, %s, %s)", \
                      nodeID, nodeName, nodeType, nodeWeight)
            self._graph.add_node(nodeID,             \
                                 nName   = nodeName, \
                                 nType   = nodeType, \
                                 nWeight = nodeWeight)
        else:
            log.debug("Already existing node: (%s, %s, %s %s)", \
                      nodeID, nodeName, nodeType, nodeWeight)


    def _addEdge(self, rFrom, rTo, rID, rType, rWeight):
        if not self._graph.has_edge(rFrom, rTo, key = rID):
            log.debug("Adding edge : (%s, %s, %s, %s, %s)", \
                      rFrom, rTo, rID, rType, rWeight)
            self._graph.add_edge(rFrom, rTo,      \
                                 key     = rID,   \
                                 rType   = rType, \
                                 rWeight = rWeight)
        else:
            log.debug("Already existing edge: (%s, %s, %s, %s, %s)", \
                      rID, rType, rWeight)


    def _addNeighbourhood(self, nID, neighbourhood):
        for entry in neighbourhood:
            self._addNode(entry["rOther"], entry["N.nName"], \
                          entry["N.nType"], entry["N.nWeight"])
        for entry in neighbourhood:
            self._addEdge(nID, entry["rOther"], entry["R.rID"], \
                          entry["R.rType"], entry["R.rWeight"])


    def _updatePaths(self):
        for i in xrange(len(self._hints)):
            source = self._hints[i]
            for j in xrange(i + 1, len(self._hints)):
                target = self._hints[j]
                path = all_simple_paths(self._graph, source, target, L)
                self._paths[(source, target)] = sorted(list(path), key = len)


    def drawGraph(self):
        lbls = {}
        for node in self._graph.nodes():
            lbls[node] = self._graph.node[node]["nName"]
        nx.draw_graphviz(self._graph, prog = "twopi",       \
                         with_labels = True, labels = lbls)
        path = "{0}.png".format(len(self._hints))
        plt.savefig(path)
        return path


    def dumpGraph(self):
        path = "{0}.graphml".format(len(self._hints))
        nx.write_graphml(self._graph, path)
        return path
