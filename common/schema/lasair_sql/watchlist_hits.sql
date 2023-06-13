CREATE TABLE IF NOT EXISTS watchlist_hits(
`diaObjectId` bigint,
`wl_id` int,
`cone_id` bigint,
`arcsec` float,
`name` varchar(80),
PRIMARY KEY (`diaObjectId`, `cone_id`)
)
