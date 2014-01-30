#!/usr/bin/python
# -*- coding: utf-8 -*-

# ############################################################################
# sqliteDB.py
# Authors:
#   * -kc- <kevin.cousot at gmail.com>
#   * Rider Carrion <rider.carrion at gmail.com>
# Description: 
# ============================================================================
# Notes:
#
# ############################################################################

import logging as log
import sqlite3

FILTERED_NODETYPES = [6, 7, 8, 9, 10, 18, 36, 666]
FILTERED_RELATIONTYPES = [12, 29, 29, 45, 46, 47, 48, 66, 105, 666, 777, \
                          997, 998, 1000, 1001, 1002, 2001]


def listGen(l):
    for element in l:
        yield (element,)


class SQLiteDB:


    def __init__(self, path, foreignKeysPragma = True):
        self._path = path
        self._con = sqlite3.connect(self._path)
        if self._isConnected():
            log.info("Connected to %s", self._path)
            self._con.text_factory = str
            self._con.row_factory = sqlite3.Row
            if foreignKeysPragma:
                self._turnOnFK()
            log.debug("Creating table filteredNodeTypes")
            self._createFilteredNodeTypesTbl()
            log.debug("Creating table filteredRelationTypes")
            self._createFilteredRelationTypesTbl()
            log.debug("Setting node type filters")
            self.setFilteredNodeTypes(FILTERED_NODETYPES)
            log.debug("Setting relation type filters")
            self.setFilteredRelationTypes(FILTERED_RELATIONTYPES)
        else:
            msg = "Could not connect to {0}".format(self._path)
            log.critical(msg)
            raise Exception(msg)


    def _isConnected(self):
        try:
            cur = self._con.cursor()
            cur.execute("SELECT nID FROM nodes LIMIT 1")
            data = cur.fetchone()[0]
            return True
        except Exception as e:
            self._con.close()
            self._con = None
            return False


    def _turnOnFK(self):
        log.info("Turning on foreign keys constraints")
        cur = self._con.cursor()
        cur.execute("PRAGMA foreign_keys = ON")


    def _createFilteredNodeTypesTbl(self):
        cur = self._con.cursor()
        script = "DROP TABLE IF EXISTS filteredNodeTypes; "              \
                 "CREATE TABLE filteredNodeTypes ( "                     \
                 "    ntType INTEGER, "                                  \
                 "    FOREIGN KEY(ntType) REFERENCES nodeTypes(ntType) " \
                 ");"
        cur.executescript(script)


    def _createFilteredRelationTypesTbl(self):
        cur = self._con.cursor()
        script = "DROP TABLE IF EXISTS filteredRelationTypes; "              \
                 "CREATE TABLE filteredRelationTypes ( "                     \
                 "    rtType INTEGER, "                                      \
                 "    FOREIGN KEY(rtType) REFERENCES relationTypes(rtType) " \
                 ");"
        cur.executescript(script)


    def setFilteredNodeTypes(self, types):
        cur = self._con.cursor()
        script = "INSERT INTO filteredNodeTypes VALUES (?)"
        cur.executemany(script, listGen(FILTERED_NODETYPES))
        self._con.commit()


    def setFilteredRelationTypes(self, types):
        cur = self._con.cursor()
        script = "INSERT INTO filteredRelationTypes VALUES (?)"
        cur.executemany(script, listGen(FILTERED_RELATIONTYPES))
        self._con.commit()


    def queryNodeIDByName(self, name):
        cur = self._con.cursor()
        cur.execute("SELECT nID FROM nodes " \
                    "WHERE  nName LIKE :name ",
                    {"name" : name})
        return cur.fetchall()


    def queryNeighboursByID(self, nID):
        cur = self._con.cursor()
        cur.execute("SELECT DISTINCT R.rTo AS ngID "                 \
                    "FROM relations AS R, "                          \
                    "     nodes     AS N "                           \
                    "WHERE R.rFrom = :rFrom "                        \
                    "AND   R.rType NOT IN "                          \
                    "  (SELECT rtType FROM filteredRelationTypes) "  \
                    "AND   N.nID = R.rTo "                           \
                    "AND   N.nType NOT IN "                          \
                    "  (SELECT ntType FROM filteredNodeTypes) "      \
                    "UNION "                                         \
                    "SELECT DISTINCT R.rFrom AS ngID "               \
                    "FROM relations AS R, "                          \
                    "     nodes     AS N "                           \
                    "WHERE R.rTo  = :rTo "                           \
                    "AND   R.rType NOT IN "                          \
                    "  (SELECT rtType FROM filteredRelationTypes) "  \
                    "AND   N.nID  = R.rFrom "                        \
                    "AND   N.nType NOT IN "                          \
                    "  (SELECT rtType FROM filteredRelationTypes)",
                    {"rFrom" : nID, "rTo" : nID})
        return cur.fetchall()


    def queryNodeNeighbourhoodByID(self, nID):
        cur = self._con.cursor()
        cur.execute("SELECT DISTINCT "                                 \
                    "  R.rID, R.rTo AS rOther, R.rType, R.rWeight, "   \
                    "  N.nName, N.nType, N.nWeight "                   \
                    "FROM nodes     AS N, "                            \
                    "     relations AS R "                             \
                    "WHERE R.rFrom = :nID "                            \
                    "AND R.rType NOT IN "                              \
                    "  (SELECT rtType FROM filteredRelationTypes) "    \
                    "AND N.nID = R.rTo "                               \
                    "AND N.nType NOT IN "                              \
                    "  (SELECT ntType FROM filteredNodeTypes) "        \
                    "UNION "                                           \
                    "SELECT DISTINCT "                                 \
                    "  R.rID, R.rFrom AS rOther, R.rType, R.rWeight, " \
                    "  N.nName, N.nType, N.nWeight "                   \
                    "FROM nodes     AS N, "                            \
                    "     relations AS R "                             \
                    "WHERE R.rTo = :nID "                              \
                    "AND R.rType NOT IN "                              \
                    "  (SELECT rtType FROM filteredRelationTypes) "    \
                    "AND N.nID = R.rFrom "                             \
                    "AND N.nType NOT IN "                              \
                    "  (SELECT ntType FROM filteredNodeTypes) ",
                    {"nID" : nID})
        return cur.fetchall()


    def queryNodeByID(self, nID):
        cur = self._con.cursor()
        cur.execute("SELECT nID, nName, nType, nWeight " \
                    "FROM nodes "                        \
                    "WHERE nID = :nID",
                    {"nID" : nID})
        return cur.fetchone()


    def queryNodesByID(self, nIDs):
        cur = self._con.cursor()
        cur.executemany("SELECT nID, nName, nType, nWeight " \
                        "FROM nodes "                        \
                        "WHERE nID = (?)",
                        listGen(nIDs))
        return cur.fetchall()


    def queryEdgeDatas(self, rID):
        cur = self._con.cursor()
        cur.execute("SELECT rID, rFrom, rTo, rType, rWeight " \
                    "FROM relations "                         \
                    "WHERE rID = :rID",
                    {"rID" : rID})
        return cur.fetchone()
