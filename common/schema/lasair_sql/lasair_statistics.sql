CREATE TABLE lasair_statistics (
    nid int NOT NULL,
    name VARCHAR(32),
    value FLOAT DEFAULT 0,
    PRIMARY key (nid,name)
);
