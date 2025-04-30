from src import db_connect


def add_annotator_metadata(
        annotators,
        remove_duplicates=False):
    """*add extra metadata to the annotators and return a list of annotator dictionaries*

    **Key Arguments:**

    - `annotators` -- a list of annotator objects
    - `remove_duplicates` -- remove duplicate annotators. Default *False*

    **Usage:**

    ```python
    annotatorDicts = add_annotator_metadata(annotators)
    ```
    """

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

    updatedAnnotators = []
    for anDict, an in zip(annotators.values(), annotators):
        # ADD LIST USER
        anDict['user'] = f"{an.user.first_name} {an.user.last_name}"
        anDict['profile_image'] = an.user.profile.image_b64
        updatedAnnotators.append(anDict)

        query = 'SELECT count(*) AS count FROM annotations WHERE topic="'
        query += anDict["topic"] + '"'
        cursor.execute(query)
        for row in cursor:
            anDict['count'] = row['count']
    return updatedAnnotators
