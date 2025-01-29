CREATE TABLE IF NOT EXISTS diaForcedSource(
"diaForcedSourceId" bigint,
"diaObjectId" bigint,
"ra" double,
"decl" double,
"visit" bigint,
"detector" int,
"psfFlux" float,
"psfFluxErr" float,
"midpointMjdTai" double,
"band" ascii,
PRIMARY KEY ("diaObjectId","midpointMjdTai")
)
