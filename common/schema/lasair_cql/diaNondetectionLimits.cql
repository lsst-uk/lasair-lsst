CREATE TABLE IF NOT EXISTS diaNondetectionLimit(
"ccdVisitId" bigint,
"midpointMjdTai" double,
"band" ascii,
"diaNoise" float,
PRIMARY KEY ("midpointMjdTai")
)
