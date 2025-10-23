import math
import sys
sys.path.append('../common')
import settings


def run_crossmatch(msl, radius, wl_id, batchSize=5000, wlMax=False):
    """ Delete all the hits and remake.
    """

    from HMpTy.mysql import conesearch
    from fundamentals.logs import emptyLogger
    from fundamentals.mysql import database, readquery, writequery, insert_list_of_dictionaries_into_database_tables
    from collections import defaultdict

    dbSettings = {
        'host': settings.DB_HOST,
        'user': settings.DB_USER_READWRITE,
        'port': settings.DB_PORT,
        'password': settings.DB_PASS_READWRITE,
        'db': 'ztf'
    }
    dbConn = database(
        log=emptyLogger(),
        dbSettings=dbSettings
    ).connect()

    # GRAB ALL SOURCES IN THE WATCHLIST
    sqlQuery = f"""
        SELECT cone_id, ra,decl, name, radius  FROM watchlist_cones WHERE wl_id={wl_id}
    """
    wlCones = readquery(
        log=emptyLogger(),
        sqlQuery=sqlQuery,
        dbConn=dbConn
    )
    # WATCHLIST COUNT
    n_cones = len(wlCones)

    if wlMax and n_cones > wlMax:
        return -1, f"A full watchlist match can only be run for watchlists with less than {wlMax} objects."

    # TRASH PREVIOUS MATCHES
    sqlQuery = f"""DELETE FROM watchlist_hits WHERE wl_id={wl_id}"""
    writequery(
        log=emptyLogger(),
        sqlQuery=sqlQuery,
        dbConn=dbConn
    )

    # GROUP SOURCES BY RADIUS
    grouped_by_radius = defaultdict(list)
    for s in wlCones:
        if not s["radius"]:
            s["radius"] = radius
        grouped_by_radius[s["radius"]].append(s)

    # CREATE BATCHES WHERE EACH BATCH CONTAINS ITEMS WITH THE SAME RADIUS
    batches_by_radius = []
    for radius, sources in grouped_by_radius.items():
        for i in range(0, len(sources), batchSize):
            batch = sources[i:i + batchSize]
            batches_by_radius.append((radius, batch))


    # SPLIT INTO BATCHES
    theseBatches = []
    for radius, groupbatch in batches_by_radius:
        gbTotal = len(groupbatch)
        gbBatches = int(gbTotal / batchSize)
        start = 0
        end = 0
        for i in range(gbBatches + 1):
            end = end + batchSize
            start = i * batchSize
            thisBatch = groupbatch[start:end]
            if len(thisBatch):
                theseBatches.append(thisBatch)

    n_hits = 0
    wlMatches = []
    for batch in theseBatches:
        # DO THE CONESEARCH
        
        raList, decList, nameList, coneIdList, radiusList = zip(*[(s["ra"], s["decl"], s["name"], s["cone_id"], s["radius"]) for s in batch])
        cs = conesearch(
            log=emptyLogger(),
            dbConn=dbConn,
            tableName="objects",
            columns="objectId",
            ra=raList,
            dec=decList,
            raCol="ramean",
            decCol="decmean",
            radiusArcsec=radiusList[0],
            separations=True,
            distinct=False,
            sqlWhere="",
            closest=False,
            htmColumns="htm16"
        )
        matchIndies, matches = cs.search()

        if len(matchIndies):
            n_hits += len(matchIndies)

            # ADD IN ORIGINAL DATA TO LIST OF MATCHES
            raList, decList, nameList, coneIdList = zip(*[(raList[i], decList[i], nameList[i], coneIdList[i]) for i in matchIndies])
            # VALUES TO ADD TO DB

            for r, d, n, c, m in zip(raList, decList, nameList, coneIdList, matches.list):
                keepDict = {
                    "wl_id": wl_id,
                    "cone_id": c,
                    "arcsec": m["cmSepArcsec"],
                    "name": n,
                    "objectId": m["objectId"]
                }
                wlMatches.append(keepDict)

            # tableData = matches.table(filepath=None)
            # print(tableData)

    if len(wlMatches):
        # USE dbSettings TO ACTIVATE MULTIPROCESSING - INSERT LIST OF DICTIONARIES INTO DATABASE
        insert_list_of_dictionaries_into_database_tables(
            dbConn=dbConn,
            log=emptyLogger(),
            dictList=wlMatches,
            dbTableName="watchlist_hits",
            dateCreated=False,
            batchSize=200000,
            dbSettings=dbSettings
        )

    message = f"{n_hits} ZTF objects have been associated with the {n_cones} sources in this watchlist"
    print(message)
    return n_hits, message


if __name__ == "__main__":
    try:
        wl_id = int(sys.argv[1])
    except:
        print('Usage: python3 run_crossmatch.py wl_id')
        sys.exit()
    radius = 3  # arcseconds

    # SETUP ALL DATABASE CONNECTIONS

    run_crossmatch(None, radius, wl_id)
