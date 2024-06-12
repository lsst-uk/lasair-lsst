CREATE TABLE IF NOT EXISTS diaForcedSources(
diaForcedSourceId bigint,
diaObjectId bigint,
ra double,
decl double,
visit bigint,
detector int,
psfFlux float,
psfFluxErr float,
midpointMjdTai double,
band ascii,
PRIMARY KEY (diaObjectId,midPointMjdTai)
)
