"""Helpers for showing a user's marks beside a table of objects."""
import sys

from src import annotate_util

sys.path.append('../common')


def marks_for_table(user, table):
    """*fetch the marks a user holds over the objects of one result table*

    One bounded query per table render, never one per row. Result tables cap at
    1000 rows, so the `IN` list stays small however large the user's mark set
    grows.

    **Key Arguments:**

    - `user` -- the viewer, marked or anonymous
    - `table` -- the rows about to be rendered

    **Return:**

    - `marks` -- `{diaObjectId: 'favourite'|'hidden'}`, empty for an anonymous
      viewer or a table with no `diaObjectId`

    **Usage:**

    ```python
    marks = marks_for_table(request.user, table)
    ```
    """
    if not table or not user.is_authenticated:
        return {}

    diaObjectIds = [row['diaObjectId'] for row in table if row.get('diaObjectId') is not None]
    if not diaObjectIds:
        return {}

    return annotate_util.marks_for_objects(annotate_util.tag_topic(user.username), diaObjectIds)
