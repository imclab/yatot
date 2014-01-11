#!/usr/bin/python
# -*- coding: utf-8 -*-

# ############################################################################
# sqliteImporter.py
# Authors:
#   * -kc- <kevin.cousot at gmail.com>
#   * Rider Carrion <rider.carrion at gmail.com>
# Description: 
# ============================================================================
# Notes:
#
# ############################################################################

import re
import sys
import codecs
import sqlite3

# globales ==================================================================

# "constants" ---------------------------------------------------------------

G_RE_NODE      = re.compile(r"eid=(?P<nID>-?\d+)\|n=\"(?P<nName>[^\"]*)\"\|t=(?P<nType>-?\d+)\|w=(?P<nWeight>-?\d+)")
G_RE_REL       = re.compile(r"rid=(?P<rID>-?\d+)\|n1=(?P<rFrom>-?\d+)\|n2=(?P<rTo>-?\d+)\|t=(?P<rType>-?\d+)\|w=(?P<rWeight>-?\d+)")

G_RE_RELMETA   = re.compile(r"\d+ occurrences of relations (?P<rtName>[^ ]+) \(t=(?P<rtType>-?\d+) nom_etendu=\"(?P<rtEName>[^\"]*)\" info=\"(?P<rtInfo>[^\"]*)\"\)")
G_RE_NODEMETA  = re.compile(r"\d+ occurrences of nodes (?P<ntName>[^ ]+) \(t=(?P<ntType>-?\d+)\)")

G_COMMENT      = "//"
G_META         = "///"

G_TURNON_FOREIGNKEYS = "PRAGMA foreign_keys = {0}"

G_INSERT_RT    = "INSERT INTO relationTypes (rtType, rtName, rtEName, rtInfo) VALUES (?,?,?,?)"
G_INSERT_NT    = "INSERT INTO nodeTypes (ntType, ntName) VALUES (?,?)"

G_INSERT_N     = "INSERT INTO nodes (nID, nName, nType, nWeight) VALUES (?,?,?,?)"
G_INSERT_R     = "INSERT INTO relations (rID, rFrom, rTo, rType, rWeight) VALUES (?,?,?,?,?)"

G_COMMIT_STEP  = 10000

# variables -----------------------------------------------------------------

g_lexicalNetwork = None
g_dbConn         = None

# core ======================================================================

# data base -----------------------------------------------------------------

def insertRelationType(rtType, rtName, rtEName, rtInfo):
    global g_dbConn
    t = (rtType, rtName, rtEName, rtInfo)
    cur = g_dbConn.cursor()
    try:
        cur.execute(G_INSERT_RT, t)
    except Exception as e:
        errmsg = e.message + " (rtType: {0})".format(rtType)
        sys.stderr.write(errmsg + "\n")
        
def insertNodeType(ntType, ntName):
    global g_dbConn
    t = (ntType, ntName)
    cur = g_dbConn.cursor()
    try:
        cur.execute(G_INSERT_NT, t)
    except Exception as e:
        errmsg = e.message + " (ntType: {0})".format(ntType)
        sys.stderr.write(errmsg + "\n")

def insertNode(nId, nName, nType, nWeight):
    global g_dbConn
    t = (nId, nName, nType, nWeight)
    cur = g_dbConn.cursor()
    try:
        cur.execute(G_INSERT_N, t)
    except Exception as e:
        errmsg = e.message + " (nID: {0})".format(nId)
        sys.stderr.write(errmsg + "\n")

def insertRelation(rId, rFrom, rTo, rType, rWeight):
    global g_dbConn
    t = (rId, rFrom, rTo, rType, rWeight)
    cur = g_dbConn.cursor()
    try:
        cur.execute(G_INSERT_R, t)
    except Exception as e:
        errmsg = e.message + " (rID: {0}, rFrom: {1}, rTo: {2})".format(rId, rFrom, rTo)
        sys.stderr.write(errmsg + "\n")

def connect2sqlitedb(dbPath, foreignKeysPragma):
    conn = sqlite3.connect(dbPath)
    if foreignKeysPragma:
        cur = conn.cursor()
        cur.execute(G_TURNON_FOREIGNKEYS.format("ON"))
        sys.stderr.write("Foreign keys pragma turned on \n")
    return conn
         
# reading -------------------------------------------------------------------

def readMeta(line):
    match = G_RE_RELMETA.match(line)
    if match != None:
        insertRelationType(match.group("rtType"), match.group("rtName"), match.group("rtEName"), match.group("rtInfo"))
    else:
        match = G_RE_NODEMETA.match(line)
        if match != None:
            insertNodeType(match.group("ntType"), match.group("ntName"))
        else:
            errmsg = u"[ERR] Unexpected metaline: `{0}`".format(line)
            sys.stderr.write(errmsg + "\n")

def readStandard(line):
    match = G_RE_NODE.match(line)
    if match != None:
        insertNode(match.group("nID"), match.group("nName"), match.group("nType"), match.group("nWeight"))
    else:
        match = G_RE_REL.match(line)
        if match != None:
            insertRelation(match.group("rID"), match.group("rFrom"), match.group("rTo"), match.group("rType"), match.group("rWeight"))
        else:
            errmsg = u"[ERR] Unexpected standard line: `{0}`".format(line)
            sys.stderr.write(errmsg + "\n")

def importLexicalNetwork(lnPath, dbPath):
    global g_lexicalNetwork
    global g_dbConn
    g_lexicalNetwork = codecs.open(lnPath, "r", "utf-8");
    g_dbConn = connect2sqlitedb(dbPath, True)
    lineno = 1
    for line in g_lexicalNetwork:
        if line[-1] == '\n':
            line = line[:-1]
        if len(line) != 0:
            if line[0:3].startswith(G_META):
                readMeta(line[4:])
            elif line[0:2].startswith(G_COMMENT):
                pass
            else:
                readStandard(line)
        lineno = lineno + 1
        if lineno % G_COMMIT_STEP == 0:
#            print lineno, "..."
            g_dbConn.commit()
    g_dbConn.commit()

# entry point ===============================================================

def main():
    if len(sys.argv) == 1:
        print "Syntaxe: {0} lexicalnet.txt sqliteDB".format(sys.argv[0])
    else:
        importLexicalNetwork(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
