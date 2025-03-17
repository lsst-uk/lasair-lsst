import json, sys

def write_lasair_schema(_name, fields):
    ''' Writes out the list of fields into a file as a Lasair Schema File
    '''
    tok = _name.split('.')
    name = tok[-1]
    name = name + 's'   #  Lasair has the plural convention for tables
    f = open('lsst_schema/' + name + '.py', 'w')
    f.write('schema = ' + json.dumps(
        {"name":name, "fields":fields, "indexes":[]}, indent=2)
        )
    f.close()

def process_fields(fields):
    ''' The fields from Rubin look like either null or this. 
    Given that SQL/CQL allows NULL by default, we don't need to be explicit about this
    '''
    new_fields = []
    for field in fields:
        name = field['name']
        type = field['type']
        if isinstance(type, str):
            pass
        elif isinstance(type, list) and len(type) == 2 and type[0] == 'null':
            type = type[1]
        else:
            print('Error in process_fields: ', type)
        new_field = {'name':name, 'type':type}
        if 'doc' in field:
            new_field['doc'] = field['doc']
        new_fields.append(new_field)

    return new_fields

def write_lasair_schemas(avscfilename):
    ''' Extract the multiple definitions from the .avsc file
    '''
    s = json.loads(open(avscfilename, 'r').read())
    for field in s['fields']:
        print(field['name'])
        type = field['type']

        # This object is just a primitive, for example alertID is a long
        if isinstance(type, str):
            print('    %s type %s' % (field['name'], type))

        # A dictionary that includes some fields
        elif isinstance(type, dict):
            name = type['name']
            fields = process_fields(type['fields'])
            print('    %s %s has %d fields' % (name, type['type'], len(fields)))
            write_lasair_schema(name, fields)

        # A list length 2 is to say it can be NULL or something
        elif isinstance(type, list) and len(type) == 2 and type[0] == 'null':
            innertype = type[1]

            # This object is just a primitive, for example cutoutImage is bytes
            if isinstance(innertype, str):
                print('    is null or %s' % innertype)

            # A dictionary that includes some fields
            elif isinstance(innertype, dict):

                # Can have several of these
                if innertype['type'] == 'array':
                    items = innertype['items']

                    # This object is just a primitive
                    if isinstance(items, str):
                        print('    is null or array of %s' % items)

                    # A dictionary that includes some fields
                    elif isinstance(items, dict):
                        name = items['name']
                        fields = process_fields(items['fields'])
                        print('    is null or array of %s with %d fields' % (name, len(fields)))
                        write_lasair_schema(name, fields)

                    # Ooops whats this now?
                    else:
                        print('Error:' + items)

                # A dictionary that includes some fields
                elif innertype['type'] == 'record':
                    fields = process_fields(innertype['fields'])
                    name = innertype['name']
                    print('    %s is null or has %d fields' % (name, len(fields)))
                    write_lasair_schema(name, fields)

                # Ooops whats this now?
                else:
                    print('Error:' + innertype)
            # Ooops whats this now?
            else:
                print('Error:' + innertype)
        # Ooops whats this now?
        else:
            print('Error:' + type)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        avscfilename = sys.argv[1]
    else:
        avscfilename = 'alert-lsst.avsc'
    write_lasair_schemas(avscfilename)
