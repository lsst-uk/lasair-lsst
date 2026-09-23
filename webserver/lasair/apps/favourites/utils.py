"""Helpers for showing a user's marks beside a table of objects."""
import sys
sys.path.append('../common')

from src import annotate_util


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


def suppress_hidden(user, table):
    """*remove a user's hidden objects from a table of results*

    Used where the result set is not built by `build_query`, so the SQL
    exclusion cannot apply — the search page is the one such surface.

    **Key Arguments:**

    - `user` -- the viewer, marked or anonymous
    - `table` -- the rows about to be rendered

    **Return:**

    - `kept` -- the rows to show
    - `marks` -- the marks held over those rows
    - `omitted` -- how many rows were removed

    **Usage:**

    ```python
    results, marks, omitted = suppress_hidden(request.user, results)
    ```
    """
    marks = marks_for_table(user, table)
    if not marks:
        return table, marks, 0

    kept = [row for row in table
            if marks.get(row.get('diaObjectId')) != annotate_util.MARK_HIDDEN]
    return kept, marks, len(table) - len(kept)
