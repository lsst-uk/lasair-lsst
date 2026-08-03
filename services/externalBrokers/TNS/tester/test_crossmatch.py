"""
ssh lasair-lsst-dev-backend_db-0
sudo bash
mysql -u root
GRANT ALL PRIVILEGES ON test.* TO 'ztf'@'%';
MariaDB [test]> desc objects;
| diaObjectId | bigint(20) | NO   | PRI | NULL    |       |
| ra          | double     | YES  |     | NULL    |       |
| decl        | double     | YES  |     | NULL    |       |
| htm16       | bigint(20) | NO   |     | NULL    |       |

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

import sys
import mysql.connector

sys.path.insert(0, '../../../../common')
import settings as real_settings

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
    cursor = msl.cursor(buffered=True, dictionary=True)

    tns_name = 'apple'
    myRA    = 53.090594
    myDecl  = -29.651906
    myHTM16 = 38585371763
    myName  = 'roy'
    myWl_id = 1
    radius  = 5.0

    cleanup = True

    query = 'REPLACE INTO objects (diaObjectId, ra, decl, htm16) '
    query += f'VALUES (1, {myRA}, {myDecl}, {myHTM16})' 
    #print(query)
    cursor.execute(query)

    query = 'REPLACE INTO watchlist_cones (name, ra, decl, radius, wl_id) '
    query += f'VALUES ("{myName}", {myRA}, {myDecl}, {radius}, {myWl_id})'
    #print(query)
    cursor.execute(query)
    msl.commit()

    nhit = tns_name_crossmatch(msl, tns_name, myRA, myDecl, radius)
    print(f'Found {nhit} hits')

    if cleanup:
        query = 'DELETE FROM watchlist_cones WHERE wl_id = 1'
        cursor.execute(query)
        query = 'DELETE FROM objects WHERE diaObjectId = 1'
        cursor.execute(query)
        query = 'DELETE FROM watchlist_hits WHERE name="{myName}"'
        cursor.execute(query)
        msl.commit()

    if nhit == 1: exit(0)   # success, found the hit
    if nhit == 0: exit(1)   # fail





