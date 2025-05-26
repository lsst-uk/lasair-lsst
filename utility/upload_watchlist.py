import sys
sys.path.append('../common')
from src import db_connect

wl_id = int(sys.argv[1])
file = open(sys.argv[2])
cones = file.read()
coneLines = cones.split('\n')
count = len(coneLines)
print('found %d cones' % len(coneLines))

chunksize = 1000
msl = db_connect.remote()
cursor = msl.cursor(buffered=True)

cone_list = []
for line in coneLines:
    if len(line) == 0:
        continue
    if line[0] == '#':
        continue
    line = line.replace('|', ',')
    tok = line.split(',')
    if len(tok) < 3:
        print(f'Bad line (not RA,Dec,Name): {line}\n')
        continue
    try:
        ra = float(tok[0])
        dec = float(tok[1])
        objectId = tok[2].strip()
        if len(tok) >= 4 and len(tok[3].strip()) > 0 and tok[3].strip().lower() != "none":
            radius = float(tok[3])
        else:
            radius = 'NULL'
        cone_list.append(f'("{objectId}", {ra}, {dec}, {radius}, {wl_id})')
    except Exception as e:
        print(f'Bad line {len(cone_list)}: {line}\n{str(e)}')

print('found %d good cones' % len(cone_list))

chunks = 1 + int(len(cone_list) / chunksize)
for i in range(chunks):
    print(i)
    s = ','.join(cone_list[(i * chunksize): ((i + 1) * chunksize)])
    if len(s) > 0:
        query = 'INSERT INTO watchlist_cones (name, ra, decl, radius, wl_id) VALUES ' + s
        cursor.execute(query)
msl.commit()

