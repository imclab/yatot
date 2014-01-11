-- File: createDB.sql
-- ---------------------------------------------------------------------------
-- Creates the database for the JDM lexical network.
-- ---------------------------------------------------------------------------

DROP TABLE IF EXISTS nodeTypes;
DROP TABLE IF EXISTS relationTypes;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS relations;

CREATE TABLE nodes
(
    nID     INTEGER    PRIMARY KEY AUTOINCREMENT,
    nName   TEXT,
    nType   INTEGER,
    nWeight REAL,
    FOREIGN KEY(nType) REFERENCES nodeTypes(ntType)
);

CREATE TABLE relations
(
    rID     INTEGER    PRIMARY KEY AUTOINCREMENT,
    rFrom   INTEGER,
    rTo     INTEGER,
    rType   INTEGER,
    rWeight REAL,
    FOREIGN KEY(rFrom) REFERENCES nodes(nID),
    FOREIGN KEY(rTo)   REFERENCES nodes(nID),
    FOREIGN KEY(rType) REFERENCES relationTypes(rtType)
);

CREATE TABLE nodeTypes
(
    ntType  INTEGER    PRIMARY KEY AUTOINCREMENT,
    ntName  TEXT
);

CREATE TABLE relationTypes
(
    rtType  INTEGER    PRIMARY KEY AUTOINCREMENT,
    rtName  TEXT,
    rtEName TEXT,
    rtInfo  TEXT
);