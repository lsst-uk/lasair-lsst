"""
ssh lasair-lsst-dev-backend_db-0
sudo bash
mysql -u root
GRANT ALL PRIVILEGES ON test.* TO 'ztf'@'%';
MariaDB [test]> desc objects;
| diaObjectId | bigint(20) | NO   | PRI | NULL    |       |
| ra          | double     | YES  |     | NULL    |       |
| decl        | double     | YES  |     | NULL    |       |

MariaDB [test]> desc watchlist_cones;
| cone_id | int(11)     | NO   | PRI | NULL    | auto_increment |
| name    | varchar(32) | YES  |     | NULL    |                |
| ra      | double      | YES  |     | NULL    |                |
| decl    | double      | YES  |     | NULL    |                |
| radius  | double      | YES  |     | NULL    |                |
| wl_id   | int(11)     | YES  |     | NULL    |                |

MariaDB [test]> desc watchlist_hits;
| diaObjectId | bigint(20)  | NO   | PRI | NULL    |       |
| wl_id       | int(11)     | YES  |     | NULL    |       |
| cone_id     | bigint(20)  | NO   | PRI | NULL    |       |
| arcsec      | float       | YES  |     | NULL    |       |
| name        | varchar(80) | YES  |     | NULL    |       |

MariaDB [test]> desc watchlists;
| wl_id         | int(11)     | NO   | PRI | NULL    | auto_increment |
| date_modified | datetime(6) | YES  |     | NULL    |                |
"""

#import settings

import sys
sys.path.insert(0, '../../../../common')
print(sys.path)
import settings as real_settings
import mysql.connector
sys.path.append('..')
from tns_crossmatch import tns_name_crossmatch

if __name__ == "__main__":
    config = {
        'user'    : real_settings.DB_USER_READWRITE,
        'password': real_settings.DB_PASS_READWRITE,
        'host'    : real_settings.DB_HOST,
        'port'    : real_settings.DB_PORT,
        'database': 'test'
    }
    msl =  mysql.connector.connect(**config)

    tns_name = 'apple'
    myRA = 170.0
    myDecl = 20.0
    radius = 5.0
    tns_name_crossmatch(msl, tns_name, myRA, myDecl, radius)


