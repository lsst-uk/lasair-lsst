CREATE TABLE IF NOT EXISTS diaForcedSources(
diaForcedSourceId bigint,
ccdVisitId bigint,
diaObjectId bigint,
midPointTai double,
filterName ascii,
psFlux float,
psFluxErr float,
totFlux float,
totFluxErr float,
PRIMARY KEY (diaObjectId)
)
