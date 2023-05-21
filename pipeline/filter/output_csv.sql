SELECT * FROM objects INTO OUTFILE '/data/mysql/objects.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

SELECT * FROM sherlock_classifications INTO OUTFILE '/data/mysql/sherlock_classifications.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

SELECT * FROM watchlist_hits INTO OUTFILE '/data/mysql/watchlist_hits.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

SELECT * FROM area_hits INTO OUTFILE '/data/mysql/area_hits.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';
