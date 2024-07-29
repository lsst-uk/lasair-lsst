import sys
import json, time, math, datetime
sys.path.append('../../common/src')
import manage_status

def check_status(nid, nalert):
    """check_status.
    Use manage_status with alerts ingested today and alerts produced by ZTF

    Args:
        nid: night-id associated with this ingestion
        nalert: number of alerts ingested in this batch
    """

#    update_time = datetime.datetime.utcnow().isoformat()
#    update_time = update_time.split('.')[0]
    
    ms = manage_status.manage_status()
    ms.add({'today_ingest': nalert}, nid)
