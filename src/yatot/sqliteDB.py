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
# * Il faudrait implémenter un système de filtre sur les types de noeuds et
#   de relations. Tout les types ne sont pas pertinents comme n_question, 
#   r_chunk_sujet etc ...
#   A priori, ce qu'il faudrait faire :
#   créer deux tables temporaires filteredNodeTypes et filteredRelationTypes,
#   et les utiliser lors des requetes, par exemple
#   SELECT ...
#   FROM relations AS R
#   WHERE R.rType NOT IN (SELECT * FROM filteredRelationTypes)
# ############################################################################

import logging as log
import sqlite3

class SQLiteDB:


    def __init__(self, path, foreignKeysPragma = True):
        self._path = path
        self._con = sqlite3.connect(self._path)
        if self._isConnected():
            log.info("Connected to %s", self._path)
            if foreignKeysPragma:
                self._turnOnFK()
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


    def queryNeighboursByID(self, nID):
        cur = self._con.cursor()
        cur.execute("SELECT rTo AS neighbour "   \
                    "FROM relations "            \
                    "WHERE rFrom = :rFrom "      \
                    "UNION "                     \
                    "SELECT rFrom AS neighbour " \
                    "FROM relations "            \
                    "WHERE rTo = :rTo",
                    {"rFrom" : nID, "rTo" : nID})
        return cur.fetchall()


    def queryNodeDatas(self, nID):
        cur = self._con.cursor()
        cur.execute("SELECT nID, nName, nType, nWeight " \
                    "FROM nodes "                        \
                    "WHERE nID = :nID",
                    {"nID" : nID})
        return cur.fetchone()


    def queryEdgeDatas(self, rID):
        cur = self._con.cursor()
        cur.execute("SELECT rID, rFrom, rTo, rType, rWeight " \
                    "FROM relations "                         \
                    "WHERE rID = :rID",
                    {"rID" : rID})
        return cur.fetchone()
