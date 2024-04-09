CREATE TABLE IF NOT EXISTS mma_area_hits(
`diaObjectId` bigint,
`mw_id` int,
`contour` float,
`distance` float,
`probdens2` float,
`probdens3` float,
PRIMARY KEY (`diaObjectId`),
KEY `mw_id_idx` (`mw_id`),UNIQUE KEY `diaObjectId_mw_id_idx` (`diaObjectId`,`mw_id`)
)
