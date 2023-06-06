import os, json
from getJump       import getJump
from fitExp        import fitExp
from fitBazinExpBB import fitBazinExpBB

samplesdirs = ['DP02', 'BazinBB', 'plasticc', 'sampleAlerts']
filterNames = ['u', 'g', 'r', 'i', 'z', 'y']

A = 1 
T = 4
t0 = 0
k = 0.1
kr = 0.01
kf = 0.005
sigma = 0.1
def r(q):
    if q: return '%6.3f'%q
    else: return '      '

for samples in samplesdirs:
    f = open('features_%s.html'%samples, 'w')
    for _file in sorted(os.listdir(samples)):
        if not _file.endswith('.json'):
            continue
        tok = _file.split('.')
        file = tok[0]
        try:
            alert = json.loads(open(samples+'/'+file+'.json').read())
        except Exception as e:
            print(file, e)
            continue
    
        f.write('<h4>%s %s</h4>' % (samples, file))
        f.write('<table><tr><td><img src=%s_plots/%s.png></td>\n<td><pre>' % (samples, file))

        dict = getJump(alert, 1.0)
        f.write('jump: %s\n' % r(dict['jump']))

        dict = fitExp(alert, [A,k], sigma)
        for fn in filterNames:
            f.write('Exp %s: k: %s pm %s\n' % (fn, r(dict[fn+'_k']), r(dict[fn+'_kerr'])))

        dict = fitBazinExpBB(alert, [A, T, kr-kf], [A, T, t0, kr, kf], sigma)
        if dict:
            if 'kf' in dict:
                f.write('Bazin  k: %s pm %s | kf: %s pm %s | T: %s pm %s\n' 
                % (r(dict['kr']), r(dict['krerr']), r(dict['kf']), r(dict['kferr']), r(dict['T']), r(dict['Terr'])))
            else:
                f.write('ExpBB  k: %s pm %s | T: %s pm %s' 
                % (r(dict['k']), r(dict['kerr']), r(dict['T']), r(dict['Terr'])))

        f.write('</pre></td></tr></table><hr/>\n')
    f.close()
