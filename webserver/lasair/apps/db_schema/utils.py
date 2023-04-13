"""
Schema based utils
"""
import importlib


def get_schema(
    schema_name
):
    """*return schema as a list of dictionaries for give schema name*

    **Key Arguments:**

    - `schema_name` -- name of the database table to return schema for (list of dictionaries)

    **Usage:**

    ```python
    from lasair.apps.db_schema import get_schema
    scheme = get_schema('objects')
    ```           
    """
    schema_package = importlib.import_module('schema.' + schema_name)
    return schema_package.schema['fields']


def get_schema_dict(schema_name):
    """*return a database schema as a dictionary*

    **Key Arguments:**

    - `schema_name` -- name of the database table

    **Usage:**

    ```python
    from lasair.apps.db_schema import get_schema
    schemaDict = get_schema_dict("objects")
    ```           
    """
    schemaDict = {k["name"]: k["doc"] for k in get_schema(schema_name)}
    return schemaDict


def get_schema_for_query_selected(
    selected
):
    """*parse the selected component of a user's query and return a lite-schema as a dictionary (to be presented on webpages)*

    **Key Arguments:**

    - `selected` -- the 'selected' component of a user query

    **Usage:**

    ```python
    from lasair.apps.db_schema import get_schema_for_query_selected
    schemaDict = get_schema_for_query_selected(selected)
    ```           
    """

    # GET ALL SCHEMA IN SINGLE DICTIONARY
    schemas = {
        'objects': get_schema_dict('objects'),
        'sherlock_classifications': get_schema_dict('sherlock_classifications'),
        'crossmatch_tns': get_schema_dict('crossmatch_tns'),
        'annotations': get_schema_dict('annotations'),
        'crossmatch_tns': get_schema_dict('crossmatch_tns')
    }

    # GENERATE A TABLE SPECIFIC SCHEMA
    tableSchema = {}
    tableSchema["mjdmin"] = "earliest detection in alert packet"
    tableSchema["mjdmax"] = "most recent detection in alert packet"
    tableSchema["UTC"] = "time Lasair issued detection alert"

    for select in selected.split(","):
        select = select.strip()
        if " " not in select:
            select = select.split(".")
            listName = []
            if len(select) == 2 and select[0].lower() in [k.lower() for k in schemas.keys()]:
                if select[1] == "*":
                    if select[0] in schemas.keys():
                        for k, v in schemas[select[0]].items():
                            tableSchema[k] = v
                else:
                    if select[0] in schemas.keys() and select[1] in schemas[select[0]].keys():
                        tableSchema[select[1]] = schemas[select[0]][select[1]]

    return tableSchema
