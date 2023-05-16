CREATE TABLE IF NOT EXISTS objects(
`diaObjectId` bigint NOT NULL,
`htm16` bigint NOT NULL,
`ra` double,
`decl` double,
`taimax` double,
`taimin` double,
`ncand` int,
`ncand_7` int,
PRIMARY KEY (diaObjectId),
KEY htmid16idx (htm16),
KEY idxRadecTai (radecTai)
)
