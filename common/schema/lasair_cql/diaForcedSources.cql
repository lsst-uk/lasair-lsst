CREATE TABLE IF NOT EXISTS diaForcedSources(
diaForcedSourceId bigint,
diaObjectId bigint,
ccdVisitId bigint,
psfFlux float,
psfFluxErr float,
x float,
y float,
flags bigint,
midpointMjdTai double,
band ascii,
PRIMARY KEY (diaObjectId,midPointMjdTai)
)
