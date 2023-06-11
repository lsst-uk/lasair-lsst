import matplotlib.pyplot as plt
import numpy as np
import os, sys, json

color = {
   "u": "#9900cc",
   "g": "#3366ff",
   "r": "#33cc33",
   "i": "#ffcc00",
   "z": "#ff0000",
   "y": "#cc6600",
}

def plottype(ax, type, diaList):
    i = 0
    for filter in color.keys():
        i += 1
        _mjd  = []
        _flux = []
        _ferr = []
        for ds in diaList:
            if ds['filterName'] == filter:
                _mjd.append(ds['midPointTai'])
                if type != 'nondet': 
                    _flux.append(ds['psFlux'])
                    _ferr.append(ds['psFluxErr'])
                else:
                    _flux.append(ds['diaNoise'])
        _mjd  = np.array(_mjd)
        _flux = np.array(_flux)
        _ferr = np.array(_ferr)
        if type == 'det':
            ax.errorbar(_mjd, _flux, yerr=_ferr, \
                c=color[filter], fmt='o', markersize=6, label=filter)
        elif type == 'fdet':
            ax.errorbar(_mjd, _flux, yerr=_ferr, \
                c=color[filter], fmt='D', markersize=6)
        else:
            ax.scatter(_mjd, _flux, s = 6, marker='v')

def plotit(ax, filename):
    lc = json.loads(open(filename).read())
    diaObject                 = lc['diaObject']

    plottype(ax, 'det',   lc['diaSourcesList'])
    plottype(ax, 'fdet',  lc['diaForcedSourcesList'])
    plottype(ax, 'nondet',lc['diaNondetectionLimitsList'])

    ax.legend()
    ax.set_xlabel('Time in days')
    ax.set_ylabel('Flux in nJansky')

#########################
if len(sys.argv) > 1: 
    category = sys.argv[1]
else:
    print('Usage: python3 plots.py <category>')
    sys.exit()
os.system('mkdir ' + category + '_plots')

for file in os.listdir(category):
    gfile = category + '/' + file
    if gfile.endswith('.json'):
        print(gfile)
        fig, ax = plt.subplots()
        plotit(ax, gfile)
        plt.title(file + ' (' + category + ')')
#        plt.show()
        plt.savefig(category + '_plots/' + file.replace('json', 'png'))
        plt.close()
