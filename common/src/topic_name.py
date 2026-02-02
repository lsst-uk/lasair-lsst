def topic_name(userid, name):
    """generate a kafka topic name based on userid and query name.

    **Key Arguments:**

        - `userid` -- the users unique ID
        - `name` -- the name given to the filter

    """
    name = ''.join(e for e in name if e.isalnum() or e == '_' or e == '-' or e == '.')
    # Make sure name is shorter than 128 characters
    if len(name) > 128:
        nname = name[0:64]+name[-64:]
    return 'lasair_' + str(userid) + nname

