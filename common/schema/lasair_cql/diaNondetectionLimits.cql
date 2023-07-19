CREATE TABLE IF NOT EXISTS diaNondetectionLimits(
ccdVisitId bigint,
midPointTai double,
filterName ascii,
diaNoise float,
diaObjectId bigint,
PRIMARY KEY (diaObjectId)
)
