def cql_type(primtype):
    if   primtype == 'float':    return ' float'
    elif primtype == 'double':   return ' double'
    elif primtype == 'int':      return ' int'             # 31 bit with sign
    elif primtype == 'long':     return ' bigint'          # 63 bit with sign
    elif primtype == 'bigint':   return ' bigint'          # 63 bit with sign
    elif primtype == 'string':   return ' ascii'
    elif primtype == 'char':     return ' ascii'
    elif primtype == 'boolean':  return ' boolean'
    elif primtype == 'blob':     return ' blob'
    else:
        print('ERROR unknown CQL type ', primtype)
        return None

def sql_type(primtype):
    if   primtype == 'float':    return ' float'
    elif primtype == 'double':   return ' double'
    elif primtype == 'int':      return ' int'             # 31 bit with sign
    elif primtype == 'long':     return ' bigint'          # 63 bit with sign
    elif primtype == 'bigint':   return ' bigint'          # 63 bit with sign
    elif primtype == 'date':     return ' datetime(6)'
    elif primtype == 'string':   return ' varchar(16)'
    elif primtype == 'bigstring':return ' varchar(80)'
    elif primtype == 'text':     return ' text'
    elif primtype == 'timestamp':return ' timestamp'
    elif primtype == 'JSON':     return ' JSON'
    else: 
        print('ERROR unknown SQL type ', primtype)
        return None

def default(primtype):
    if   primtype == 'float':    return 0.0
    elif primtype == 'double':   return 0.0
    elif primtype == 'int':      return 0
    elif primtype == 'long':     return 1234
    elif primtype == 'bigint':   return 1234
    elif primtype == 'string':   return 'hello'
    elif primtype == 'bigstring':return 'hello'
    elif primtype == 'text':     return 'hello'
    else: return None
