def create_insert_sherlock(ann: dict):
    """create_insert_sherlock.
    Makes the insert query for the sherlock classification

    Args:
        ann:
    """
    # all the sherlock attrs that we want for the database
    attrs = [
        "classification",
        "diaObjectId",
        "association_type",
        "catalogue_table_name",
        "catalogue_object_id",
        "catalogue_object_type",
        "raDeg",
        "decDeg",
        "separationArcsec",
        "northSeparationArcsec",
        "eastSeparationArcsec",
        "physical_separation_kpc",
        "direct_distance",
        "distance",
        "best_distance",
        "best_distance_flag",
        "best_distance_source",
        "z",
        "photoZ",
        "photoZErr",
        "Mag",
        "MagFilter",
        "MagErr",
        "classificationReliability",
        "major_axis_arcsec",
        "annotator",
        "additional_output",
        "description",
        "summary",
    ]
    sets = {}
    for key in attrs:
        sets[key] = None
    for key, value in ann.items():
        if key in attrs and value:
            sets[key] = value

    # this hack adds back in the deprecated 'distance' as 'best_distance'
    if 'best_distance' in ann:
        sets['distance'] = ann['best_distance']

    if 'description' in attrs and 'description' not in ann:
        sets['description'] = 'no description'
    # Build the query
    query_list = []
    query = 'REPLACE INTO sherlock_classifications SET '
    for key, value in sets.items():
        if value is None:
            query_list.append(key + '=NULL')
        else:
            query_list.append(key + '=' + "'" + str(value).replace("'", '') + "'")
    query += ',\n'.join(query_list)
    return query

