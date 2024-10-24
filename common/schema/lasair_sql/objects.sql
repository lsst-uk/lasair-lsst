CREATE TABLE IF NOT EXISTS objects(
`htm16` bigint NOT NULL,
`diaObjectId` bigint NOT NULL,
`ra` double,
`decl` double,
`g_psfFluxMean` float,
`g_psfFluxMeanErr` float,
`r_psfFluxMean` float,
`r_psfFluxMeanErr` float,
`nSources` int NOT NULL,
`nuSources` int,
`ngSources` int,
`nrSources` int,
`niSources` int,
`nzSources` int,
`nySources` int,
`maxTai` double,
`minTai` double,
`uPSFlux` float,
`gPSFlux` float,
`rPSFlux` float,
`iPSFlux` float,
`zPSFlux` float,
`yPSFlux` float,
`absFlux` float,
`fluxJump` float,
`uExpRate` float,
`gExpRate` float,
`rExpRate` float,
`iExpRate` float,
`zExpRate` float,
`yExpRate` float,
`uExpRateErr` float,
`gExpRateErr` float,
`rExpRateErr` float,
`iExpRateErr` float,
`zExpRateErr` float,
`yExpRateErr` float,
`bazinExpRiseRate` float,
`bazinExpFallRate` float,
`bazinExpTemp` float,
`bazinExpRiseRateErr` float,
`bazinExpFallRateErr` float,
`bazinExpTempErr` float,
`timestamp` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (diaObjectId),
KEY htmid16idx (htm16),
KEY idxMaxTai (maxTai)
)
