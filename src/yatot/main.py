#!/usr/bin/python
# -*- coding: utf-8 -*-

# ############################################################################
# main.py
# Authors:
#   * -kc- <kevin.cousot at gmail.com>
#   * Rider Carrion <rider.carrion at gmail.com>
# Description: 
# ============================================================================
# Notes:
#
# ############################################################################

import logging  as log
import argparse as ap

import yatot
import sqliteDB

# logging ====================================================================

def initLog(level):
    lvl = None
    if level == "DEBUG":
        lvl = log.DEBUG
    elif level == "INFO":
        lvl = log.INFO
    elif level == "WARNING":
        lvl = log.WARNING
    elif level == "ERROR":
        lvl = log.ERROR
    elif level == "CRITICAL":
        lvl = log.CRITICAL
    log.basicConfig(format = "%(levelname)s:%(module)s:%(message)s",
                    level = lvl)

# arg parsing ================================================================

def buildParser():
    loggingLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    parser = ap.ArgumentParser(prog ="yatot")
    parser.add_argument("jdmdb",
                        help = "JeuxDeMots SQLite3 database")
    parser.add_argument("--logging",
                        choices = loggingLevels,
                        default = "DEBUG",
                        metavar = "",
                        help    = "log level. Allowed values: " + ", ".join(loggingLevels))
    return parser

# body =======================================================================

def main():
    parser = buildParser()
    args = parser.parse_args()
    initLog(args.logging)
    db = sqliteDB.SQLiteDB(args.jdmdb)
    y = yatot.Yatot(db)
    y.play()

if __name__ == "__main__":
    main()
