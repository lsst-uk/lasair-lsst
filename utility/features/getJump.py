import math
import numpy as np

# ugrizy filter names
filterNames = ['u', 'g', 'r', 'i', 'z', 'y']

def getJump(alert, days):
    sources = alert['diaForcedSourcesList'] + alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midPointTai'])

    tobs = [s['midPointTai']    for s in sources]
    fobs = [s['psFlux']         for s in sources]

    max_tobs  = tobs[-1]
    max_flux = 0

    dict = {'jump': None}
    n = 0
    fluxsum = fluxsum2 = 0.0
    last_fobs = 0
    for i in range(len(tobs)):
        # statistics of those before 'days' days ago
        if max_tobs - tobs[i] > days:
#            print(fobs[i])
            fluxsum  += fobs[i]
            fluxsum2 += fobs[i]*fobs[i]
            n += 1
        else:
#            print('*', fobs[i])
            if fobs[i] > max_flux:
                max_flux = fobs[i]
    if n < 4:
        return dict
           
    meanf = fluxsum/n
    var = fluxsum2/n - meanf*meanf
    sd = math.sqrt(var)
#    print(meanf, sd)
    jump = (max_flux - meanf)/sd
    if jump < 0:
        jump = 0
    return {'jump': jump}

if __name__ == '__main__':
    import os, sys, json

    if len(sys.argv) > 1:
        samples = sys.argv[1]
    else:
        print('Must add name of sample set')
        sys.exit()
    for file in sorted(os.listdir(samples)):
        if not file.endswith('.json'):
            continue
        try:
            alert = json.loads(open(samples+'/'+file).read())
        except Exception as e:
            print(file, e)
            continue

        dict = getJump(alert, 1.0)
        print(file, dict)
