CREATE TABLE IF NOT EXISTS mma_area_hits(
`diaObjectId` bigint,
`mw_id` int,
`skyprob` float,
`distsigma` float,
PRIMARY KEY (`diaObjectId`),
KEY `mw_id_idx` (`mw_id`),UNIQUE KEY `diaObjectId_mw_id_idx` (`diaObjectId`,`mw_id`)
)
