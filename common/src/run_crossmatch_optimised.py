import math
import sys
sys.path.append('../common')
import settings

def run_crossmatch(msl, radius, wl_id, batchSize=50000, wlMax=False):
    
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
        if s["radius"] > 1800.:
            s["radius"] = 1800.
        s["coarseRadius"] = None
        grouped_by_radius[s["radius"]].append(s)
    
    ## MAKE COARSER BINNING FOR HETROGENEOUS RADII
    if len(grouped_by_radius) > 10:
        coarse = True
        grouped_by_radius = defaultdict(list)
        for s in wlCones:
            if not s["radius"]:
                s["radius"] = radius
            if s["radius"] > 1800.:
                s["radius"] = 1800.
            stages = [10, 100, 300, 500, 1000, 1500, 1800]
            for stage in stages:
                if s["radius"] <= stage:
                    s["coarseRadius"] = math.ceil(s["radius"] / stage) * stage
                    break
                s["coarseRadius"] = math.ceil(s["radius"] / 1800) * 1800
            grouped_by_radius[s["coarseRadius"]].append(s)
    else:
        coarse = False

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
        batchSize = int(5e7 // (radius * radius))
        if batchSize > 50000:
            batchSize = 50000
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
    from fundamentals import fmultiprocess
    results = fmultiprocess(log=emptyLogger(), function=run_crossmatch_batch,
                          inputArray=theseBatches, poolSize=False, timeout=300, turnOffMP=False, progressBar=True, coarse=coarse, wl_id=wl_id)
    for result in results:
        if result:
            wlMatches.extend(result)
            n_hits += len(result)

    if len(wlMatches):
        # USE dbSettings TO ACTIVATE MULTIPROCESSING - INSERT LIST OF DICTIONARIES INTO DATABASE
        insert_list_of_dictionaries_into_database_tables(
            dbConn=dbConn,
            log=emptyLogger(),
            dictList=wlMatches,
            dbTableName="watchlist_hits",
            dateCreated=False,
            batchSize=200000,
            replace=True,
            dbSettings=dbSettings
        )

    message = f"{n_hits} LSST objects have been associated with the {n_cones} sources in this watchlist"
    print(message)
    return n_hits, message


def run_crossmatch_batch(batch, log, wl_id, coarse=False):
    from HMpTy.mysql import conesearch
    from fundamentals.mysql import database
    dbSettings = {
        'host': settings.DB_HOST,
        'user': settings.DB_USER_READWRITE,
        'port': settings.DB_PORT,
        'password': settings.DB_PASS_READWRITE,
        'db': 'ztf'
    }
    dbConn = database(
        log=log,
        dbSettings=dbSettings
    ).connect()


    wlMatches = []
    # DO THE CONESEARCH
    raList, decList, nameList, coneIdList, coarseRadiusList, radiusList = zip(*[(s["ra"], s["decl"], s["name"], s["cone_id"], s["coarseRadius"], s["radius"]) for s in batch])
    if coarse:
        thisRadius = coarseRadiusList[0]
    else:
        thisRadius = radiusList[0]
    cs = conesearch(
        log=log,
        dbConn=dbConn,
        tableName="objects",
        columns="diaObjectId",
        ra=raList,
        dec=decList,
        raCol="ra",
        decCol="decl",
        radiusArcsec=thisRadius,
        separations=True,
        distinct=False,
        sqlWhere="",
        closest=False,
        htmColumns="htm16"
    )
    matchIndies, matches = cs.search()
    if len(matchIndies):
        # ADD IN ORIGINAL DATA TO LIST OF MATCHES
        raList, decList, nameList, coneIdList, radiusList = zip(*[(raList[i], decList[i], nameList[i], coneIdList[i], radiusList[i]) for i in matchIndies])
        # VALUES TO ADD TO DB

        for r, d, n, c, rad, m in zip(raList, decList, nameList, coneIdList, radiusList, matches.list):
            if coarse and m["cmSepArcsec"] > rad:
                continue
            keepDict = {
                "wl_id": wl_id,
                "cone_id": c,
                "arcsec": m["cmSepArcsec"],
                "name": n,
                "diaObjectId": m["diaObjectId"]
            }
            wlMatches.append(keepDict)
    return wlMatches

if __name__ == "__main__":
    try:
        wl_id = int(sys.argv[1])
    except:
        print('Usage: python3 run_crossmatch.py wl_id')
        sys.exit()
    radius = 3  # arcseconds

    # SETUP ALL DATABASE CONNECTIONS

    run_crossmatch(None, radius, wl_id)
