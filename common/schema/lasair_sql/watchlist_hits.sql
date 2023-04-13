CREATE TABLE IF NOT EXISTS watchlist_hits(
`diaObjectId` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
`wl_id` int,
`cone_id` bigint,
`arcsec` float,
`name` varchar(80),
PRIMARY KEY (`diaObjectId`, `cone_id`)
)
