"""
Schema based utils
"""
import importlib
import settings


def get_schema(
    schema_name,
    extended=False,
    explodeSections=False
):
    """*return schema as a list of dictionaries for give schema name*

    **Key Arguments:**

    - `schema_name` -- name of the database table to return schema for (list of dictionaries)
    - `extended` -- get the extend schema if it exists (instead of the core schema). Default **False**
    - `explodeSections` -- if the schema comes in sections, then collapse the scheme into just the raw field (remove sections)

    **Usage:**

    ```python
    from lasair.apps.db_schema import get_schema
    scheme = get_schema('diaObjects')
    ```           
    """
    schema_package = importlib.import_module(\
            'schema.%s.%s' % (settings.SCHEMA_VERSION,  schema_name))

    if extended:
        if 'ext_fields' in schema_package.schema:
            fields = schema_package.schema['ext_fields']
        else:
            fields = []
    else:
        fields = schema_package.schema['fields']

    def populate_schema(feilds):
        schema = []
        if not len(feilds):
            return schema
        if "section" in feilds[0]:
            thisSection = feilds[0]
            thisSection["fields"] = []
            feilds = feilds[1:]
        else:
            thisSection = {"section": "main", "doc": "main section", "fields": []}

        for f in feilds:
            if "section" in f:
                schema.append(thisSection)
                thisSection = f
                thisSection["fields"] = []
            elif 'name' in f:
                thisSection["fields"].append(f)
        schema.append(thisSection)
        return schema

    schema = populate_schema(fields)

    if explodeSections:
        schema[:] = [s["fields"] for s in schema]
        schema = [item for sublist in schema for item in sublist]

    return schema


def get_schema_dict(schema_name):
    """*return a database schema as a dictionary*

    **Key Arguments:**

    - `schema_name` -- name of the database table

    **Usage:**

    ```python
    from lasair.apps.db_schema import get_schema
    schemaDict = get_schema_dict("diaObjects")
    ```           
    """
    schemaDict = {}

    for k in get_schema(schema_name, explodeSections=True):
        if 'doc' in k:
            schemaDict[k['name']] = k['doc']
        else:
            schemaDict[k['name']] = ''
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
        'objects': get_schema_dict('diaObjects'),
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
