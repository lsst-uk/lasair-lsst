var JS9Prefs = {
    "globalOpts": {
        "helperType": "none",
        "helperPort": 2718,
        "helperCGI": "./cgi-bin/js9/js9Helper.cgi",
        "debug": 1,
        "loadProxy": true,
        "workDir": "./tmp",
        "workDirQuota": 100,
        "dataPath": "$HOME/Desktop:$HOME/data",
        "analysisPlugins": "./analysis-plugins",
        "analysisWrappers": "./analysis-wrappers"
    },
    "imageOpts": {
        "colormap": "magma",
        "scale": "linear",
        "scaleclipping": "zscale",
        "zscalecontrast": 0.2, // default from ds9
        "zscalesamples": 600, // default from ds9
        "zscaleline": 120, // default from ds9
        "contrast": 0.5, // default color contrast
    }
}
