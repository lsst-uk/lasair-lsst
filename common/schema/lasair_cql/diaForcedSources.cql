CREATE TABLE IF NOT EXISTS diaForcedSources(
diaForcedSourceId bigint,
diaObjectId bigint,
ra double,
dec double,
visit bigint,
detector int,
psfFlux float,
psfFluxErr float,
midpointMjdTai double,
band ascii,
PRIMARY KEY (diaObjectId,midPointMjdTai)
)
