CREATE TABLE IF NOT EXISTS diaNondetectionLimits(
ccdVisitId bigint,
midpointMjdTai double,
band ascii,
diaNoise float,
PRIMARY KEY (midpointMjdTai)
)
