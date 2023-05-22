import os, sys, json
fr = 'tmp'
to = 'samples'
for filename in sorted(os.listdir(fr)):
    gfile = fr + '/' + filename
    f = json.loads(open(gfile).read())

    j = {
        'diaObject'                :f['diaObject'],
        'diaSourcesList'           :f['diaSource.List'],
        'diaForcedSourcesList'     :f['diaForcedSourcesList'],
        'diaNondetectionLimitsList':f['diaNondetectionLimitsList'],
    }

    gfile = to + '/' + filename
    g = open(gfile, 'w')
    g.write(json.dumps(j, indent=2))
    g.close()
