SELECT * FROM objects INTO OUTFILE '/var/lib/mysql-files/objects.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

SELECT * FROM sherlock_classifications INTO OUTFILE '/var/lib/mysql-files/sherlock_classifications.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

SELECT * FROM watchlist_hits INTO OUTFILE '/var/lib/mysql-files/watchlist_hits.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

SELECT * FROM area_hits INTO OUTFILE '/var/lib/mysql-files/area_hits.txt' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';
