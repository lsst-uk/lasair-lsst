CREATE TABLE IF NOT EXISTS cutouts(
cutoutId ascii,
objectId bigint,
imjd int,
cutoutimage blob,
PRIMARY KEY ((imjd, cutoutId))
)
