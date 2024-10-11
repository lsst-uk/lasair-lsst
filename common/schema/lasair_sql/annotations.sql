CREATE TABLE IF NOT EXISTS annotations(
`annotationID` int NOT NULL AUTO_INCREMENT,
`diaObjectId` bigint NOT NULL,
`topic` text,
`version` varchar(80) DEFAULT 0.1,
`timestamp` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
`classification` varchar(80) NOT NULL,
`explanation` text,
`classdict` JSON,
`url` text DEFAULT NULL,
PRIMARY KEY    (annotationID),
UNIQUE KEY     one_per_object (diaObjectId, topic),
KEY topic_idx (topic)
)
