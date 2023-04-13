import sys
sys.path.append('../common')
import settings
from src import date_nid, db_connect
from src.manage_status import manage_status

def main():
    msl = db_connect.readonly()
    if not msl:
         print("ERROR in services/TNS/poll_tns: Cannot connect to the database\n")

    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute ("select count(*) as countAnnotations from annotations")
    for row in cursor:
        countAnnotations = row['countAnnotations']
    cursor.close ()

    ms = manage_status(settings.SYSTEM_STATUS)
    nid = date_nid.nid_now()
    ms.set({'countAnnotations':countAnnotations}, nid)

if __name__ == '__main__':
    main()

