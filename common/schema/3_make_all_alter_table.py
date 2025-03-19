import os,sys

if len(sys.argv) > 2:
    schema_ver_old = sys.argv[1]
    schema_ver_new = sys.argv[2]
else:
    print('Usage: 3_make_all_alter_table.py <schema_ver_old> <schema_ver_new>')
    sys.exit()


print('MySQL databases')
s = 'python3 3_make_alter_table.py sql %s %s annotations'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py sql %s %s area_hits'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py sql %s %s crossmatch_tns'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py sql %s %s mma_area_hits'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py sql %s %s objects'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py sql %s %s sherlock_classifications'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py sql %s %s watchlist_hits'
os.system(s % (schema_ver_old, schema_ver_new))

print('Cassandra')
s = 'python3 3_make_alter_table.py cql %s %s cutouts'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py cql %s %s cutoutsByObject'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py cql %s %s diaForcedSources'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py cql %s %s diaNondetectionLimits'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py cql %s %s diaObjects'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py cql %s %s diaSources'
os.system(s % (schema_ver_old, schema_ver_new))
s = 'python3 3_make_alter_table.py cql %s %s ssObjects'
os.system(s % (schema_ver_old, schema_ver_new))


